from datetime import datetime
import uuid

from .messages.message_chain import MessageChain
from .services.context_manager import ContextManager
from .services import approval_request_service, message_service, user_service, space_service, conversation_service
from .services.documents.document_manager import DocumentManager
from .database import SessionLocal

class Conversation:
    def __init__(self, id, title, settings, message_handler, plugins=None, db=None):
        self.id = id
        self.db = db if db else SessionLocal()
        self.title = title
        self.settings = settings
        self.plugins = plugins
        self.user_message = None
        self.message_handler = message_handler
        self.document_manager = DocumentManager(id)
        self.context_manager = ContextManager(self)

        self.actions = {
            "handle_approval_response": self.handle_approval_response,
        }

    def __str__(self):
        return self.title

    async def handle_message(self, user_message=None, function_output=None):
        continue_conversation = True

        while continue_conversation:
            # Initialize a new message chain with initial messages
            context = MessageChain(system_message=self.settings['llm']['system_message'],
                                   user_message=user_message, function_output=function_output, conversation_id=self.id)

            # Add tool function definitions
            functions = [tool['definition'] for tool in self.tools]

            # Add context from snippets
            for snippet in self.snippets:
                await snippet['method'](snippet['instance'], context)

            # Complete context with past messages
            self.context_manager.generate_context(context)

            # Send complete context to the LLM for a response
            ai_response = await self.message_handler.get_ai_response(self, context, functions)

            # Save user message / tool output and AI response to database
            role = "user" if user_message else "function"
            message = user_message if user_message else function_output

            # Construct metadata
            metadata = context.get_metadata()
            
            self.save_message(role=role, content=message, conversation_id=self.id, metadata=metadata)

            follow_up_requested = False

            if ai_response:
                if ai_response['function_call']:
                    metadata.append({'function_call': ai_response['function_call']})

                self.save_message(role="assistant", content=ai_response['content'], conversation_id=self.id, metadata=metadata)

                # Handle requested tool, if any
                function_output, follow_up_requested = await self.handle_tool_requests(ai_response)

            if follow_up_requested:
                user_message = None
            else:
                return ai_response, context

    async def handle_tool_requests(self, ai_response):
        """
        Entry point for tool requests, used after each AI response
        """
        if ai_response['function_call']:
            tool_name = ai_response['function_call']['name']
            tool_args = ai_response['function_call']['arguments']
            # Find the loaded tool plugin
            for tool in self.tools:
                if tool['name'] == tool_name:
                    # Request approval if required, or process
                    if tool['settings']['requires_approval']['value']:
                        await self.request_approval(tool, tool_args)
                    else:
                        await self.message_handler.send_alert_to_ui(tool['metadata']['display_name'], self.id, "tool_start")
                        try:
                            result = await tool['method'](tool['instance'], **tool_args)
                            function_output = {"name": tool_name, "output": result}
                            await self.message_handler.send_alert_to_ui(tool['metadata']['display_name'], self.id, "tool_success")
                            return function_output, tool['settings']['follow_up_on_output']['value']
                        except Exception as e:
                            await self.message_handler.send_alert_to_ui(tool['metadata']['display_name'], self.id, "tool_error")
                            print(f"An error occurred while using tool `{tool_name}`: {e}")
                            return None, False
                    break

        return None, False

    async def request_approval(self, tool, tool_args):
        """
        Issues an approval request and sends it to the frontend
        """
        pending_request = approval_request_service.create_approval_request(self.db, self.id, tool['name'], tool_args)

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
            notification = f"Neary would like to use the **{tool['metadata']['display_name']}** tool<<args>>{table_header}\n{args_string}<</args>>"
        else:
            notification = f"Neary would like to use the **{tool['metadata']['display_name']}** tool"

        await self.message_handler.send_notification_to_ui(message=notification, conversation_id=self.id, actions=actions, save_to_db=True)

    def handle_approval_response(self, data, message_id):
        request_id = data.get("request_id")
        response = data.get("response")

        try:
            request_id = uuid.UUID(request_id)
        except ValueError:
            print("Invalid request ID")

        if response.lower() not in ["approve", "reject"]:
            print("Invalid action. Use 'approve' or 'reject'")

        approval_request = approval_request_service.get_approval_request(self.db, request_id, "pending")

        if not approval_request:
            print("Approval request not found.")

        if response.lower() == "approve":
            approval_request = approval_request_service.update_approval_request_status(self.db, approval_request, "approved")
            self.message_handler.send_status_to_ui(message={"approval_response_processed": message_id}, conversation_id=self.id)
        elif response.lower() == "reject":
            self.message_handler.send_status_to_ui(message={"approval_response_processed": message_id}, conversation_id=self.id)
            approval_request = approval_request_service.update_approval_request_status(self.db, approval_request, "rejected")

        self.process_approval(approval_request.serialize())

        message = message_service.get_message_by_id(self.db, message_id)

        if not message:
            print("Couldn't retrieve a message with ID: ", message_id)
        else:
            message_service.delete_message(self.db, message)

        return f"Request {approval_request.status}"

    async def process_approval(self, approved_request):
        status = approved_request['status']
        tool_name = approved_request['tool_name']
        tool_args = approved_request['tool_args']

        if status == 'rejected':
            content = {"name": tool_name,
                       "output": "User rejected function approval request; function not executed."}
            await self.save_message("function", content=content, conversation_id=self.id, metadata=[])
            return

        # If approved, find the loaded tool plugin
        for tool in self.tools:
            if tool['name'] == tool_name:
                await self.message_handler.send_alert_to_ui(tool['metadata']['display_name'], self.id, "tool_start")
                result = await tool['method'](tool['instance'], **tool_args)

                function_output = {"name": tool_name, "output": result}
                await self.message_handler.send_alert_to_ui(tool['metadata']['display_name'], self.id, "tool_success")

                # Call handle message if tool wants to follow-up
                if tool['settings']['follow_up_on_output']:
                    await self.handle_message(function_output=function_output)

    async def handle_action(self, name, data, message_id):
        action_handler = self.actions.get(name)
        if action_handler:
            response = await action_handler(data, message_id)
            return response
        else:
            print(f'Unrecognized action: {name}')
            raise Exception("Unrecognized action: {name}")

    def load_plugins(self):
        from .services.plugin_manager import PluginManager
        plugin_manager = PluginManager()

        self.snippets = []
        self.tools = []

        for plugin in self.plugins:
            if not plugin['is_enabled']:
                continue

            plugin_name = plugin["name"]

            # Get the plugin's functions class and method references, plus definition
            plugin_info = plugin_manager.get_plugin(plugin_name)

            # Add settings for each function, if it's loaded into memory
            all_function_settings = {
                function['name']: function['settings'] 
                for function in plugin['functions'] 
                if function['name'] in plugin_info['functions'].get(function['type']+'s', {})
            }

            for function in plugin['functions']:
                function_name = function['name']
                function_type = function['type'] + 's'

                # Check if the function name exists in the plugin_info
                if function_name in plugin_info['functions'].get(function_type, {}):
                    function_method = plugin_info['functions'][function_type][function_name]['method']
                    function_definition = plugin_info['functions'][function_type][function_name].get('definition', None)

                    # Create an instance of the plugin class
                    plugin_instance = plugin_info['class'](plugin["id"], self, all_function_settings, plugin.get("data", None))

                    # Store the function method and its instance
                    function_data = {
                        'name': function_name,
                        'instance': plugin_instance,
                        'method': function_method,
                        'definition': function_definition,
                        'settings': function['settings'],
                        'metadata': function['metadata']
                    }

                    # Append the function data to the appropriate list
                    if function_type == 'tools':
                        self.tools.append(function_data)
                    elif function_type == 'snippets':
                        self.snippets.append(function_data)
                else:
                    print (f"No matching function loaded for config entry: {function_name}")

    def get_user_profile(self):
        user = user_service.get_user_by_id(self.db, 1)
        return user.profile

    def get_space_options(self):
        spaces = space_service.get_active_spaces(self.db)
        space_options = [{"option": space.name, "value": space.id} for space in spaces]

        conversation_model = conversation_service.get_conversation_by_id(self.db, self.id)
        current_space_id = conversation_model.space_id if conversation_model else None

        return current_space_id, space_options

    def save_message(self, role, content, conversation_id, actions=None, metadata=None):
        if role == 'function':
            metadata.append({'function_name': content['name']})
            message = message_service.create_message(self.db, "function", content['output'], 
                                                    conversation_id, actions, metadata)
        elif (content and type(content) == str) or len(metadata) > 0:
            message = message_service.create_message(self.db, role, content, 
                                                    conversation_id, actions, metadata)
            conversation = conversation_service.get_conversation_by_id(self.db, conversation_id)
            conversation_service.update_conversation_timestamp(self.db, conversation)
            return message

    def save_state(self):
        conversation_model = conversation_service.get_conversation_by_id(self.db, self.id)
        if conversation_model:
            conversation_service.update_conversation_settings(self.db, conversation_model, self.settings)
