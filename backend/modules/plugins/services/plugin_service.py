from typing import TYPE_CHECKING, List

import inspect
import importlib
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from backend.plugins import BasePlugin

from modules.messages.schemas import FunctionMessage
from modules.conversations.models import ConversationModel
from modules.approvals.services.approval_service import ApprovalService

from ..models import (
    PluginModel,
    PluginInstanceModel,
    FunctionInstanceModel,
    FunctionModel,
)

if TYPE_CHECKING:
    from core.services.message_handler import MessageHandler


class PluginService:
    def __init__(self, db: Session, message_handler: "MessageHandler" = None):
        self.db = db
        self.message_handler = message_handler

    def get_plugins(self):
        return self.db.query(PluginModel).all()

    def get_plugins_by_conversation(self, conversation: ConversationModel):
        plugin_instances = conversation.plugins

        return plugin_instances

    def get_plugin_by_id(self, id: int):
        return self.db.query(PluginModel).filter(PluginModel.id == id).first()

    def get_plugin_instance_by_id(self, id: int):
        return (
            self.db.query(PluginInstanceModel)
            .filter(PluginInstanceModel.id == id)
            .first()
        )

    def get_plugin_by_name(self, plugin_name: str):
        return (
            self.db.query(PluginModel).filter(PluginModel.name == plugin_name).first()
        )

    def get_functions_by_conversation(self, conversation: ConversationModel):
        plugin_instances = conversation.plugins
        function_instances = [
            function_instance
            for plugin in plugin_instances
            for function_instance in plugin.function_instances
        ]

        return function_instances

    def get_function_by_name(self, function_name: str) -> FunctionModel:
        return self.db.query(FunctionModel).filter_by(name=function_name).first()

    def get_function_instance_by_id(self, id: int):
        return (
            self.db.query(FunctionInstanceModel)
            .filter(FunctionInstanceModel.id == id)
            .first()
        )

    def enable_plugin(self, plugin_entry: PluginModel):
        plugin_entry.is_enabled = True
        self.db.commit()

    def disable_plugin(self, plugin_entry: PluginModel):
        plugin_entry.is_enabled = False
        self.db.commit()

    def get_tool_definitions(self, plugins: List[PluginInstanceModel]):
        functions = []
        for plugin in plugins:
            function_instances = plugin.function_instances
            for instance in function_instances:
                if instance.function.type == "tool":
                    function_dict = {}
                    function_dict["name"] = instance.function.name
                    function_dict["description"] = instance.function.llm_description

                    function_dict["parameters"] = {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    }

                    # Iterate over each parameter in the tool
                    parameters = instance.function.parameters or {}
                    for param_name, param_data in parameters.items():
                        function_dict["parameters"]["properties"][
                            param_name
                        ] = self._parse_parameter(param_data)

                        # Check if the parameter is required
                        if param_data.get("required"):
                            function_dict["parameters"]["required"].append(param_name)
                    if function_dict:
                        functions.append(function_dict)

        return functions

    def _parse_parameter(self, param_data):
        # Prepare the base parameter structure
        parameter = {"type": param_data.get("type")}

        # Add a description if it exists and is not None, otherwise exclude the field
        description = param_data.get("description")
        if description is not None:
            parameter["description"] = description

        # Handle 'array' type parameters
        if param_data["type"] == "array" and "items" in param_data:
            # Ensure the 'items' structure does not contain 'null' for the 'description' field
            items_data = param_data["items"]
            items_parameter = self._parse_parameter(items_data)
            if (
                "description" in items_parameter
                and items_parameter["description"] is None
            ):
                del items_parameter[
                    "description"
                ]  # Remove the 'description' field if it's None
            parameter["items"] = items_parameter

        # Handle 'object' type parameters
        elif param_data["type"] == "object" and "properties" in param_data:
            properties = {}
            required = []
            for item_name, item_data in param_data["properties"].items():
                properties[item_name] = self._parse_parameter(item_data)
                if item_data.get("required"):
                    required.append(item_name)
            parameter["properties"] = properties
            if required:
                parameter["required"] = required

        return parameter

    async def execute_tool(
        self,
        tool_name: str,
        tool_args: dict,
        conversation: ConversationModel,
        bypass_approval=False,
    ):
        plugin_instances = conversation.plugins

        # Find the function in the conversation's list of plugins
        for plugin_instance in plugin_instances:
            for function_instance in plugin_instance.function_instances:
                if function_instance.name == tool_name:
                    tool = function_instance
                    if (
                        tool.settings_values["requires_approval"]["value"]
                        and bypass_approval is False
                    ):
                        approval_service = ApprovalService(
                            self.db, self.message_handler
                        )
                        await approval_service.request_approval(
                            tool, tool_args, conversation.id
                        )
                        return None, False
                    else:
                        await self.message_handler.send_alert_to_ui(
                            tool.function.display_name, "tool_start"
                        )
                        try:
                            tool_method = self._load_function_instance(
                                tool_name, plugin_instance, conversation
                            )
                            if inspect.iscoroutinefunction(tool_method):
                                result = await tool_method(**tool_args)
                            else:
                                result = tool_method(**tool_args)
                            await self.message_handler.send_alert_to_ui(
                                tool.function.display_name, "tool_success"
                            )
                            function_message = FunctionMessage(
                                function_call={
                                    "name": tool_name,
                                    "arguments": tool_args,
                                },
                                content=result,
                                conversation_id=conversation.id,
                            )
                            return (
                                function_message,
                                tool.settings_values["follow_up_on_output"]["value"],
                            )
                        except Exception as e:
                            await self.message_handler.send_alert_to_ui(
                                tool.function.display_name, "tool_error"
                            )
                            print(
                                f"An error occurred while using tool `{tool_name}`: {e}"
                            )

        return None, False

    async def add_snippets_to_context(self, context, conversation: ConversationModel):
        for plugin_instance in conversation.plugins:
            for function_instance in plugin_instance.function_instances:
                if function_instance.function.type == "snippet":
                    snippet_method = self._load_function_instance(
                        function_instance.name, plugin_instance, conversation
                    )
                    if inspect.iscoroutinefunction(snippet_method):
                        await snippet_method(context)
                    else:
                        snippet_method(context)

    def _load_function_instance(self, function_name, plugin_instance, conversation):
        try:
            # Import the plugin module
            plugin_module = importlib.import_module(
                f"plugins.{plugin_instance.name}.{plugin_instance.name}"
            )

            # Find the plugin class in the module
            for name, cls in inspect.getmembers(plugin_module):
                if (
                    inspect.isclass(cls)
                    and issubclass(cls, BasePlugin)
                    and cls is not BasePlugin
                ):
                    # Compile plugin settings

                    # Create an instance of the plugin class with the provided arguments
                    class_instance = cls(
                        plugin_instance.id,
                        conversation.id,
                        PluginServices(self.db, conversation.id),
                        self._compile_settings(plugin_instance),
                        plugin_instance.data,
                    )

                    # Get the function from the class instance
                    function_instance = getattr(class_instance, function_name)

                    # Return the class instance and the function
                    return function_instance

        except Exception as e:
            print(f"Error loading plugin: {e}")

    def _compile_settings(self, plugin_instance):
        function_settings = {}
        for function_instance in plugin_instance.function_instances:
            function_settings[
                function_instance.name
            ] = function_instance.get_merged_settings()
        return function_settings

    def delete_plugin(self, plugin_entry: PluginModel):
        self.db.delete(plugin_entry)
        self.db.commit()

    def create_plugin_instance(
        self,
        plugin_name: str,
        conversation: ConversationModel,
        settings_values: dict = None,
        functions: List[dict] = [],
    ):
        plugin = self.get_plugin_by_name(plugin_name)

        if plugin:
            plugin.is_enabled = True

            plugin_instance = PluginInstanceModel(
                name=plugin.name,
                plugin=plugin,
                settings_values=settings_values or plugin.settings_metadata,
                conversation=conversation,
            )
            self.db.add(plugin_instance)
            self.db.flush()

            for function in functions:
                self.create_function_instance(
                    function_name=function["name"],
                    plugin_instance=plugin_instance,
                    settings_values=function.get("settings_values", None),
                )

            self.db.commit()

            return plugin_instance

    def create_function_instance(
        self,
        function_name: str,
        plugin_instance: PluginInstanceModel,
        settings_values: dict = None,
    ):
        function = self.get_function_by_name(function_name)

        if function:
            function_instance = FunctionInstanceModel(
                name=function.name,
                function=function,
                plugin_instance=plugin_instance,
                settings_values=settings_values or function.settings_metadata,
            )

            self.db.add(function_instance)
            self.db.commit()

    def update_plugin_instance(self, plugin_id: int, settings: dict):
        # Currently just updates settings for individual functions, as there are no plugin-level settings
        for function_name, function_settings in settings.items():
            function_instance = self.get_function_instance_by_id(
                function_settings.pop("id", None)
            )

            if function_instance:
                self.update_function_instance(function_instance, function_settings)

        self.db.commit()

    def update_function_instance(
        self, function_instance: FunctionInstanceModel, settings: dict
    ):
        for setting_key in settings:
            if isinstance(settings[setting_key], dict):
                value = settings[setting_key].get("value", settings[setting_key])
            else:
                value = settings[setting_key]
            function_instance.settings_values[setting_key]["value"] = value

        flag_modified(function_instance, "settings_values")
        self.db.commit()
        self.db.refresh(function_instance)

    def delete_function_instance(
        self, function_name: str, conversation: ConversationModel
    ):
        functions = self.get_functions_by_conversation(conversation)

        function_instance = next(
            (function for function in functions if function.name == function_name),
            None,
        )

        if function_instance:
            self.db.delete(function_instance)
            self.db.commit()

    def save_plugin_instance_state(
        self,
        id: int,
        new_data: dict,
        new_settings: dict,
    ):
        plugin_instance = self.get_plugin_instance_by_id(id)

        plugin_instance.data = new_data

        function_instances = (
            self.db.query(FunctionInstanceModel)
            .filter(FunctionInstanceModel.plugin_instance_id == plugin_instance.id)
            .all()
        )

        for instance in function_instances:
            if instance.name in new_settings:
                self.update_function_instance(instance, new_settings[instance.name])

        self.db.commit()


class PluginServices:
    """This class contains all services that are passed to the plugin on instantiation"""

    def __init__(self, db: Session, conversation_id: int = None):
        self.db = db
        self.conversation_id = conversation_id
        self._populate_service()

    def _populate_service(self):
        self._add_user_services()
        self._add_credentials_services()
        self._add_message_services()
        self._add_file_services()

    def _add_user_services(self):
        from users.services import UserService

        user_service = UserService(self.db)

        self.get_profile = user_service.get_profile
        self.get_profile_field = user_service.get_profile_field
        self.set_profile = user_service.set_profile
        self.set_profile_field = user_service.set_profile_field

    def _add_credentials_services(self):
        from modules.integrations.services.integration_service import IntegrationService

        integration_service = IntegrationService(self.db)
        self.get_credentials = integration_service.get_credentials

    def _add_message_services(self):
        from core.services.message_handler import MessageHandler

        message_handler = MessageHandler(db=self.db)
        self.send_alert_to_ui = message_handler.send_alert_to_ui
        self.send_message_to_ui = message_handler.send_message_to_ui
        self.send_file_to_ui = message_handler.send_file_to_ui

    def _add_file_services(self):
        from core.services.core_service import FileService

        file_service = FileService(conversation_id=self.conversation_id)
        self.save_file = file_service.save_file
