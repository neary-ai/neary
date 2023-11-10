from typing import TYPE_CHECKING, List

import os
import inspect
import importlib
from sqlalchemy.orm import Session

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
        if param_data["type"] == "array" and "items" in param_data:
            items_properties = self._parse_parameter(param_data["items"])
            return {"type": "array", "items": items_properties}
        elif param_data["type"] == "object" and "properties" in param_data:
            properties = {}
            required = []
            for item_name, item_data in param_data["properties"].items():
                if item_data.get("required"):
                    required.append(item_name)
                properties[item_name] = self._parse_parameter(item_data)
            return {"type": "object", "properties": properties, "required": required}
        else:
            return {
                "type": param_data.get("type"),
                "description": param_data.get("description"),
            }

    async def execute_tool(
        self,
        tool_name: str,
        tool_args: dict,
        conversation: ConversationModel,
        bypass_approval=False,
    ):
        tool = None

        plugin_instances = conversation.plugins

        # Find the function in the conversation's list of plugins
        for plugin_instance in plugin_instances:
            for function_instance in plugin_instance.function_instances:
                if function_instance.name == tool_name:
                    tool = function_instance
                    break

        if tool:
            if (
                tool.settings_values["requires_approval"]["value"]
                and bypass_approval is False
            ):
                approval_service = ApprovalService(self.db, self.message_handler)
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
                    result = await tool_method(**tool_args)
                    await self.message_handler.send_alert_to_ui(
                        tool.function.display_name, "tool_success"
                    )
                    function_message = FunctionMessage(
                        function_call={"name": tool_name, "arguments": tool_args},
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
                    print(f"An error occurred while using tool `{tool_name}`: {e}")

        return None, False

    async def add_snippets_to_context(self, context, conversation: ConversationModel):
        for plugin_instance in conversation.plugins:
            for function_instance in plugin_instance.function_instances:
                if function_instance.function.type == "snippet":
                    snippet_method = self._load_function_instance(
                        function_instance.name, plugin_instance, conversation
                    )
                    await snippet_method(context)

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
                        PluginServices(self.db),
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

    def update_function_instance(
        self, function_instance: FunctionInstanceModel, settings: dict
    ):
        for setting_key in settings:
            function_instance.settings_values[setting_key] = settings[setting_key]

        self.db.commit()

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

    def __init__(self, db: Session):
        self.db = db
        self._populate_service()

    def _populate_service(self):
        self._add_user_services()
        self._add_credentials_services()
        self._add_message_services()

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

    # def get_plugin_instances(
    #     self, plugin_instance: PluginInstanceModel, loaded_plugin: dict
    # ):
    #     tools = []
    #     snippets = []

    #     all_function_settings = {
    #         function.name: function.settings_values
    #         for function in plugin_instance.function_instances
    #         if function.name
    #         in loaded_plugin["functions"].get(function.function.type + "s", {})
    #     }

    #     for function in plugin_instance.function_instances:
    #         function_name = function.name
    #         function_type = function.function.type + "s"

    #         # Check if the function name exists in the loaded plugin
    #         if function_name in loaded_plugin["functions"].get(function_type, {}):
    #             function_method = loaded_plugin["functions"][function_type][
    #                 function_name
    #             ]["method"]
    #             function_definition = loaded_plugin["functions"][function_type][
    #                 function_name
    #             ].get("definition", None)

    #             # Create an instance of the plugin class
    #             plugin_instance = loaded_plugin["class"](
    #                 id=plugin_instance.id,
    #                 conversation_id=plugin_instance.conversation_id,
    #                 settings=all_function_settings,
    #                 data=plugin_instance.data,
    #             )

    #             # Store the function method and its instance
    #             function_data = {
    #                 "name": function_name,
    #                 "instance": plugin_instance,
    #                 "method": function_method,
    #                 "definition": function_definition,
    #                 "settings": function.settings_values,
    #                 "metadata": function.function.meta_data,
    #             }

    #             # Append the function data to the appropriate list
    #             if function_type == "tools":
    #                 tools.append(function_data)
    #             elif function_type == "snippets":
    #                 snippets.append(function_data)
    #         else:
    #             print(f"No matching function loaded for config entry: {function_name}")

    #     return tools, snippets

    # def clear_plugin_instance_data(self, plugin_instance: PluginInstanceModel):
    #     plugin_instance.data = {}
    #     self.db.commit()

    # def get_function_instance_by_name(
    #     self, function_name: str, conversation: ConversationModel
    # ) -> FunctionInstanceModel:
    #     return (
    #         self.db.query(FunctionInstanceModel).filter_by(name=function_name).first()
    #     )

    # def update_conversation_plugins(
    #     self, conversation: ConversationModel, new_plugin_data: list
    # ):
    #     existing_plugin_names = [plugin.name for plugin in conversation.plugins]
    #     new_plugin_names = [plugin["name"] for plugin in new_plugin_data]
    #     plugins_to_remove = set(existing_plugin_names) - set(new_plugin_names)

    #     self.remove_plugins(conversation, plugins_to_remove)

    #     plugin_service = plugin_services.PluginService(self.db)
    #     function_service = plugin_services.FunctionService(self.db)

    #     for plugin in new_plugin_data:
    #         plugin_instance = plugin_service.update_plugin_instance(
    #             conversation, plugin
    #         )
    #         if plugin_instance:
    #             plugin_service.enable_plugin(self.db, plugin_instance.plugin)
    #             function_service.update_function_instances(
    #                 self.db, plugin_instance, plugin["functions"]
    #             )
    #             function_service.remove_function_instances(
    #                 self.db, plugin_instance, plugin["functions"]
    #             )

    # def remove_plugins(self, conversation: ConversationModel, plugins_to_remove: set):
    #     plugin_service = plugin_services.PluginService(self.db)

    #     for plugin_name in plugins_to_remove:
    #         plugin = plugin_service.get_plugin_by_name(plugin_name=plugin_name)

    #         # Remove related instances
    #         instances = plugin.instances

    #         for instance in instances:
    #             if instance.conversation == conversation:
    #                 self.db.delete(instance)
    #                 self.db.commit()
