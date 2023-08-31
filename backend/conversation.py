from datetime import datetime
import importlib
import inspect
import json
import uuid
import re

from .messages.message_chain import MessageChain
from .services.context_manager import ContextManager
from .services.message_handler import MessageHandler
from .models.models import UserModel, MessageModel, ConversationModel, SpaceModel, ApprovalRequestModel
from .services.documents.document_manager import DocumentManager
from .services.plugin_manager import PluginManager


class Conversation:
    def __init__(self, id, title, settings, plugins=None, message_handler=None):
        self.id = id
        self.title = title
        self.settings = settings
        self.plugins = plugins
        self.user_message = None
        self.message_handler = message_handler if message_handler else MessageHandler()
        self.document_manager = DocumentManager(id)
        self.context_manager = ContextManager(self)

        self.actions = {
            "handle_approval_response": self.handle_approval_response,
        }

    def __str__(self):
        return self.title

    async def handle_message(self, user_message=None, tool_output=None):
        continue_conversation = True

        while continue_conversation:
            # Initialize a new message chain with initial messages
            context = MessageChain(system_message=self.settings['llm']['system_message'],
                                   user_message=user_message, tool_output=tool_output, conversation_id=self.id)

            # Insert available tools
            if self.tools:
                context.add_snippet(self.get_tools_str())

            # Add context from snippets
            for snippet in self.snippets:
                await snippet['method'](snippet['instance'], context)

            # Complete context with past messages
            await self.context_manager.generate_context(context)

            # Send complete context to the LLM for a response
            ai_response = await self.message_handler.get_ai_response(self, context)

            # Save user message / tool output and AI response to database
            role = "user" if user_message else "tool_output"
            message = user_message if user_message else tool_output

            await self.save_message(role=role, content=message, conversation_id=self.id)
            await self.save_message(role="assistant", content=ai_response, conversation_id=self.id, metadata=context.get_metadata())

            # Handle requested tool, if any
            tool_output, follow_up_requested = await self.handle_tool_requests(ai_response)

            if follow_up_requested:
                # Set user_message to none to process new tool output
                user_message = None
            else:
                continue_conversation = False

    def get_tools_str(self):
        tools_str = """You are a tool-assisted AI assistant. This means you can use tools, if necessary, to accomplish tasks that you wouldn't otherwise be able to accomplish as a Large Language Model.\nTo use a tool, simply append a tool request to the bottom of your response in this format: <<tool:tool_name({"tool_arg": "tool_arg_value"}). Replace 'tool_name', 'tool_arg' and 'tool_arg_value' with the values for the tool you're invoking. Here's a list of tools you have available to you:\n\n"""

        for tool in self.tools:
            tools_str += f"- {tool['metadata']['llm_description']}\n"
        
        return tools_str

    async def handle_tool_requests(self, ai_response):
        """
        Entry point for tool requests, used after each AI response
        """
        tool_request = self.extract_tool(ai_response)

        if tool_request:
            tool_name, tool_args = tool_request

            # Find the loaded tool plugin
            for tool in self.tools:
                if tool['name'] == tool_name:
                    # Request approval if required, or process
                    if tool['metadata']['settings']['requires_approval']:
                        await self.request_approval(tool, tool_args)
                    else:
                        tool_output = await tool['method'](tool['instance'], **tool_args)
                        return tool_output, tool['metadata']['settings']['follow_up_on_output']
                    break

        return None, False

    def extract_tool(self, ai_response):
        """
        Parses tool requests and provided arguments from the LLM
        TO-DO: Implement proper OpenAI function calling
        """
        tool_pattern = r'<<tool:([^(\s]+)\(([^>]*)\)>>'
        match = re.search(tool_pattern, ai_response)

        if match:
            tool_name = match.group(1)
            tool_args_json = match.group(2)

            try:
                tool_kwargs = json.loads(tool_args_json)
            except json.JSONDecodeError:
                print("No valid JSON arguments found in tool_args.")
                tool_kwargs = {}

            return tool_name, tool_kwargs

    async def request_approval(self, tool, tool_args):
        """
        Issues an approval request and sends it to the frontend
        """
        # First save the request to db
        pending_request = ApprovalRequestModel(
            conversation_id=self.id, tool_name=tool['name'], tool_args=tool_args)
        await pending_request.save()

        # Then send notification to ui
        actions = [
            {
                'type': 'function',
                'name': 'handle_approval_response',
                'label': 'Approve',
                'conversation_id': self.id,
                'data': {'request_id': str(pending_request.id), 'response': 'approve'}
            },
            {
                'type': 'function',
                'name': 'handle_approval_response',
                'label': 'Reject',
                'conversation_id': self.id,
                'data': {'request_id': str(pending_request.id), 'response': 'reject'}
            }
        ]

        args_string = '\n'.join(
            [f"| {k.replace('_', ' ').title()} | {', '.join(v) if isinstance(v, list) else v} |" for k, v in tool_args.items()])
        table_header = "| Name | Value |\n| --- | --- |"

        if args_string:
            notification = f"Neary would like to use the **{tool['metadata']['display_name']}** tool:\n{table_header}\n{args_string}."
        else:
            notification = f"Neary would like to use the **{tool['metadata']['display_name']}** tool."

        await self.message_handler.send_notification_to_ui(message=notification, conversation_id=self.id, actions=actions, save_to_db=True)

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

    async def process_approval(self, approved_request):
        tool_name = approved_request['tool_name']
        tool_args = approved_request['tool_args']

        # Find the loaded tool plugin
        for tool in self.tools:
            if tool['name'] == tool_name:
                tool_output = await tool['method'](tool['instance'], **tool_args)

                # Call handle message if tool wants to follow-up
                if tool['metadata']['settings']['follow_up_on_output']:
                    await self.handle_message(tool_output=tool_output)

    async def handle_action(self, name, data, message_id):
        action_handler = self.actions.get(name)
        if action_handler:
            response = await action_handler(data, message_id)
            return response
        else:
            print(f'Unrecognized action: {name}')
            raise Exception("Unrecognized action: {name}")

    async def load_plugins(self):
        plugin_manager = PluginManager()

        self.snippets = []
        self.tools = []

        for plugin in self.plugins:
            plugin_name = plugin["name"]
            plugin_info = plugin_manager.get_plugin(plugin_name)

            for function_name, function_info in plugin['functions'].items():
                if function_name in plugin_info['functions']:
                    function_method = plugin_info['functions'][function_name]['method']
                    function_type = plugin_info['functions'][function_name]['type']
                    function_settings = {function_name: plugin_info['functions'][function_name]['settings']}

                    # Create an instance of the plugin class
                    plugin_instance = plugin_info['class'](
                        plugin["id"], self, function_settings, plugin["data"])

                    # Store the function method and its instance
                    function_data = {
                        'name': function_name,
                        'instance': plugin_instance,
                        'method': function_method,
                        'metadata': plugin_info['functions'][function_name]
                    }

                    # Add the function data to the appropriate list
                    if function_type == 'snippet':
                        self.snippets.append(function_data)
                    elif function_type == 'tool':
                        self.tools.append(function_data)

    async def get_user_profile(self):
        user = await UserModel.first()
        return user.profile

    async def get_space_options(self):
        spaces = await SpaceModel.filter(is_archived=False)
        space_options = [{"option": space.name, "value": space.id}
                         for space in spaces]

        conversation_model = await ConversationModel.get(id=self.id)
        current_space_id = conversation_model.space_id

        return current_space_id, space_options

    async def save_message(self, role, content, conversation_id, actions=None, metadata=None):
        if content and type(content) == str:
            message = await MessageModel.create(role=role, content=content, conversation_id=conversation_id, actions=actions, metadata=metadata)
            conversation = await ConversationModel.get(id=conversation_id)
            conversation.updated_at = datetime.utcnow()
            await conversation.save()

            return message

    async def save_state(self):
        conversation_model = await ConversationModel.get(id=self.id)
        conversation_model.settings = self.settings
        await conversation_model.save()
