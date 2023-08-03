import re
import json
import uuid

from backend.programs.utils import get_local_time_str
from backend.models import ProgramModel, ApprovalRequestModel, ConversationModel, MessageModel, UserModel
from backend.messages import MessageChain
from backend.programs.tools import CoreTools
from backend.memory import BaseMemory


class BaseProgram:

    """
    The BaseProgram is subclassed by all other programs and implements basic chat functionality
    """

    def __init__(self, conversation):
        self.id = None
        self.conversation = conversation
        self.model = 'gpt-4'

        self.system_message = "You are a helpful assistant. Be succinct unless instructed otherwise."
        self.timezone = ""
        self.notepad = []

        self.custom_tools = {}
        self.toolbox = ['update_profile', 'make_a_note', 'clear_notes']
        self.tool_approval_required = True

        self.actions = {
            "handle_approval_response": self.handle_approval_response,
        }

        self.memory_config = {
            "memory_mode": "truncate",
            "token_limit": 5000,
        }
        self.memory = BaseMemory(self)

    def __str__(self):
        return self.__class__.__name__

    async def execute(self, user_message):
        # Initialize a new message chain with required messages
        messages = MessageChain(system_message=self.system_message,
                                user_message=user_message, conversation_id=user_message['conversation_id'])

        local_time_str = await get_local_time_str()
        
        if local_time_str:
            messages.user_msg(local_time_str)

        messages.user_msg(await self.get_profile_str())
        messages.user_msg(self.get_notes_str())
        messages.user_msg(self.get_tools_str())

        # Use remaining tokens to add recent messages from memory
        context = await self.memory.generate_context(messages)

        # Send complete context to the LLM for a response
        ai_response = await self.conversation.message_handler.get_ai_response(context, self.model)

        # Save user message and AI response to database
        await self.memory.save_message(user_message)
        await self.memory.save_message(ai_response)

        # Parse the AI response for tool requests
        await self.handle_tool_requests(ai_response)

        return ai_response

    """
    Specialized message generators
    TO-DO: Move elsewhere
    """

    def get_tools_str(self):
        if not self.toolbox:
            return

        tools_str = """You are a tool-assisted AI assistant. This means you can use tools, if necessary, to accomplish tasks that you wouldn't otherwise be able to accomplish as a Large Language Model.\nTo use a tool, simply append a tool request to the bottom of your response in this format: <<tool:tool_name({"tool_arg": "tool_arg_value"}). Replace 'tool_name', 'tool_arg' and 'tool_arg_value' with the values for the tool you're invoking. Here's a list of tools you have available to you:\n\n"""

        for tool_name in self.toolbox:
            if hasattr(CoreTools, tool_name):
                tool_func = getattr(CoreTools, tool_name)
            elif tool_name in self.custom_tools:
                tool_func = self.custom_tools[tool_name]
            else:
                continue

            docstring = tool_func.__doc__
            description = "No description available"

            if docstring:
                description_lines = [line.strip()
                                     for line in docstring.strip().split('\n')]
                description = description_lines[0] if description_lines else "No description available"

            tools_str += f'- {description}\n'

        return tools_str

    def get_notes_str(self):
        if len(self.notepad) > 0:
            notes_str = "The following is your Notepad. These are helpful notes you left for yourself. Refer to these as needed:\n\n"
            for note in self.notepad:
                notes_str += f"- {note}\n\n"
            return notes_str

    async def get_profile_str(self):
        user = await UserModel.first()
        if not user.profile:
            profile_str = "This user has no information in their profile. If an opportunity arises, we should collect the user's `name` and `timezone` at minimum."
        else:
            profile_str = "Here is the user's profile. Remember to tailor your answers to their information where applicable:\n\n"
            for k, v in user.profile.items():
                profile_str += f"{k}: {v}\n"
        return profile_str

    """
    Methods for handling tools
    """

    def register_tool(self, tool_name, tool_func):
        """
        Makes a custom tool (defined as a class method) available to the program
        """
        self.custom_tools[tool_name] = tool_func

    async def handle_tool_requests(self, ai_response):
        """
        Entry point for tool requests, used after each AI response
        """
        tools = self.extract_tool(ai_response)

        if tools:
            tool_name, tool_args = tools

            # If a tool is found, request approval if necessary before using
            if self.requires_approval(tool_name):
                await self.request_approval(tool_name, tool_args)
            else:
                tool_output = await self.use_tool(tool_name, tool_args)

                if tool_output is None:
                    print('Tool error: ', tool_name)
                elif type(tool_output) == str:
                    # Loop and get LLM response to tool output
                    tool_output = f"Tool output: {tool_output}"
                    tool_msg = {'role': 'user', 'content': tool_output,
                                'conversation_id': self.conversation.id}
                    messages = MessageChain(
                        system_message=self.system_message, user_message=tool_msg, conversation_id=tool_msg['conversation_id'])

                    context = await self.memory.generate_context(messages)
                    ai_response = await self.conversation.message_handler.get_ai_response(context, self.model)

                    # Save tool output and AI response to conversation
                    tool_msg['role'] = 'background'
                    await self.memory.save_message(tool_msg)
                    await self.memory.save_message(ai_response)

    def extract_tool(self, ai_response):
        """
        Parses tool requests and provided arguments from the LLM
        TO-DO: Implement proper OpenAI function calling
        """
        tool_pattern = r'<<tool:([^(\s]+)\(([^>]*)\)>>'
        match = re.search(tool_pattern, ai_response['content'])

        if match:
            tool_name = match.group(1)
            tool_args_json = match.group(2)

            try:
                tool_kwargs = json.loads(tool_args_json)
            except json.JSONDecodeError:
                print("Invalid JSON format in tool arguments")
                tool_kwargs = {}

            return tool_name, tool_kwargs

    async def use_tool(self, tool_name, tool_args):
        """
        Use the provided tool and return output. We match tool names in two ways:
        First against the general set of tools found in CoreTools, then against
        the custom tools registered in the program.
        """
        tool_func = None
        is_core_tool = False

        if tool_name in self.custom_tools:
            tool_func = self.custom_tools[tool_name]
        elif hasattr(CoreTools, tool_name):
            tool_func = getattr(CoreTools, tool_name)
            is_core_tool = True
        else:
            return None

        try:
            if is_core_tool:
                result = await tool_func(self.conversation, **tool_args)
            else:
                result = await tool_func(**tool_args)
        except Exception as e:
            print(f"Error while running the tool '{tool_name}': {e}")
            return None

        return result

    """
    Methods for handling approval requests
    """

    def requires_approval(self, tool_name):
        """
        Determines whether an an approval request needs to be issued for a given tool.
        """
        tool_func = None

        if hasattr(CoreTools, tool_name):
            tool_func = getattr(CoreTools, tool_name)
        elif tool_name in self.custom_tools:
            tool_func = self.custom_tools[tool_name]

        if tool_func and getattr(tool_func, 'requires_approval', False) and self.tool_approval_required:
            return True

        return False

    async def request_approval(self, tool_name, tool_args):
        """
        Issues an approval request and sends it to the frontend
        """
        conversation = await ConversationModel.get(id=self.conversation.id)
        recent_message = await conversation.messages.order_by("-id").first()
        pending_request = ApprovalRequestModel(
            conversation_id=self.conversation.id, message_id=recent_message.id, tool_name=tool_name, tool_args=tool_args)
        await pending_request.save()

        actions = [
            {
                'type': 'function',
                'name': 'handle_approval_response',
                'label': 'Approve',
                'conversation_id': self.conversation.id,
                'data': {'request_id': str(pending_request.id), 'response': 'approve'}
            },
            {
                'type': 'function',
                'name': 'handle_approval_response',
                'label': 'Reject',
                'conversation_id': self.conversation.id,
                'data': {'request_id': str(pending_request.id), 'response': 'reject'}
            }
        ]

        tool_name_clean = tool_name.replace('_', ' ').title()
        args_string = '\n'.join(
            [f"| {k.replace('_', ' ').title()} | {', '.join(v) if isinstance(v, list) else v} |" for k, v in tool_args.items()])
        table_header = "| Name | Value |\n| --- | --- |"

        if args_string:
            notification = f"Neary would like to use the **{tool_name_clean}** tool:\n{table_header}\n{args_string}."
        else:
            notification = f"Neary would like to use the **{tool_name_clean}** tool."

        await self.conversation.message_handler.send_notification_to_ui(notification=notification, conversation_id=self.conversation.id, actions=actions, save_to_db=True)

    async def process_approval(self, approved_request):
        conversation_id = approved_request['conversation_id']
        message_id = approved_request['message_id']
        tool_name = approved_request['tool_name']
        tool_args = approved_request['tool_args']

        tool_output = await self.use_tool(tool_name, tool_args)

        if tool_output is None:
            print('Tool error: ', tool_name)
        elif type(tool_output) == str:
            tool_output = f"Tool output: {tool_output}"
            tool_msg = {'role': 'user', 'content': tool_output,
                        'conversation_id': conversation_id}
            messages = MessageChain(system_message=self.system_message,
                                    user_message=tool_msg, conversation_id=tool_msg['conversation_id'])

            # If conversation is in the same state, pass output back to LLM for response
            conversation = await ConversationModel.get(id=approved_request['conversation_id'])
            recent_message = await conversation.messages.order_by("-id").first()
            tool_msg['role'] = 'background'

            if recent_message.id == message_id:
                context = await self.memory.generate_context(messages)
                ai_response = await self.conversation.message_handler.get_ai_response(context, self.model)

                # Save tool output and AI response to conversation
                await self.memory.save_message(tool_msg)
                await self.memory.save_message(ai_response)
            else:
                print('Conversation changed, skipping LLM response to tool output.')
                await self.memory.save_message(tool_msg)

    """
    Methods for handling actions
    """
    async def handle_action(self, name, data, message_id):
        action_handler = self.actions.get(name)

        if action_handler:
            response = await action_handler(data, message_id)
            return response
        else:
            print(f'Unrecognized action: {name}')
            raise Exception("Unrecognized action: {name}")

    """
    Action handlers
    """
    async def handle_approval_response(self, data, message_id):
        request_id = data.get("request_id")
        response = data.get("response")

        try:
            request_id = uuid.UUID(request_id)
        except ValueError:
            print("Invalid request ID")

        if response.lower() not in ["approve", "reject"]:
            print("Invalid action. Use 'approve' or 'reject'")

        approval_request = await ApprovalRequestModel.get_or_none(id=request_id, status="pending")

        if not approval_request:
            print("Approval request not found.")

        if response.lower() == "approve":
            approval_request.status = "approved"
            await self.process_approval(approval_request.serialize())
        elif response.lower() == "reject":
            approval_request.status = "rejected"

        message = await MessageModel.get_or_none(id=message_id)

        if not message:
            print("Couldn't retrieve a message with ID: ", message_id)
        else:
            await message.delete()

        await approval_request.save()

        return f"Request {approval_request.status}"

    """
    Settings & state
    """

    def get_settings(self):
        """
        Returns settings for display on the frontend
        """
        return {
            'system_message': {
                'display_name': 'Instructions',
                'value': self.system_message,
                'field': 'Textarea'
            },
            'model': {
                'display_name': 'Model',
                'value': self.model,
                'field': 'Select',
                'options': [{'option': 'GPT-4', 'value': 'gpt-4'}, {'option': 'GPT-3.5', 'value': 'gpt-3.5-turbo'}]
            },
            'token_limit': {
                'display_name': 'Token Limit',
                'value': self.memory_config['token_limit'],
                'field': 'NumberInput'
            },
            'tool_approval_required': {
                'display_name': 'Tool Approval Required',
                'value': self.tool_approval_required,
                'field': 'Checkbox'
            },
        }

    async def set_settings(self, settings):
        """
        Updates the program instance with new provided settings data
        """
        if "model" in settings:
            self.model = settings["model"]['value']
        if "system_message" in settings:
            self.system_message = settings["system_message"]['value']
        if "tool_approval_required" in settings:
            self.tool_approval_required = settings["tool_approval_required"]['value']
        if "memory_mode" in settings:
            self.memory_config['memory_mode'] = settings["memory_mode"]['value']
        if "token_limit" in settings:
            self.memory_config['token_limit'] = settings["token_limit"]['value']

        self.memory.apply_config(self.memory_config)

        await self.save_state()


    def get_program_data(self):
        return {
            'id': self.id,
            'notepad': self.notepad,
            'timezone': self.timezone
        }

    def set_program_data(self, program_data):
        if 'id' in program_data:
            self.id = program_data['id']
        if 'notepad' in program_data:
            self.notepad = program_data['notepad']
        if 'timezone' in program_data:
            self.timezone = program_data['timezone']

    async def save_state(self):
        program_model = await ProgramModel.get_or_none(id=self.id)
        program_model.settings = self.get_settings()
        program_model.state = self.get_program_data()
        await program_model.save()

    @classmethod
    async def from_json(cls, conversation, data):
        """
        We store program data and settings in the database as JSON,
        giving us more flexibility to add / change / remove items
        """
        instance = cls(conversation)
        instance.id = data['id']
        if 'state' in data and data['state']:
            instance.set_program_data(data['state'])
        if 'settings' in data and data['settings']:
            await instance.set_settings(data['settings'])
        return instance
