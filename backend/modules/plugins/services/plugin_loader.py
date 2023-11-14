import os
import inspect
import importlib
from typing import Union
from toml import load

from sqlalchemy.orm import Session
from pydantic import ValidationError

from backend.plugins import BasePlugin
from backend.plugins.schemas import PluginConfig, Tool, Snippet
from .plugin_service import PluginService
from modules.presets.services.preset_service import PresetService
from modules.integrations.services.integration_service import IntegrationService

from ..models import (
    PluginModel,
    FunctionModel,
)


class PluginLoader:
    def __init__(self, db: Session):
        self.db = db
        self.default_plugins = ["essentials", "document_search"]
        self.plugin_service = PluginService(self.db)

    def load_plugins(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        plugins_dir = os.path.join(backend_dir, "plugins")

        for plugin_name in os.listdir(plugins_dir):
            if not plugin_name.startswith("_") and os.path.isdir(
                os.path.join(plugins_dir, plugin_name)
            ):
                self.load_plugin(plugin_name)

    def load_plugin(self, plugin_name):
        try:
            validated_config = None
            # Import the plugin module
            plugin_module = importlib.import_module(
                f"plugins.{plugin_name}.{plugin_name}"
            )

            # Find the plugin class in the module
            for name, cls in inspect.getmembers(plugin_module):
                if (
                    inspect.isclass(cls)
                    and issubclass(cls, BasePlugin)
                    and cls is not BasePlugin
                ):
                    # Load and validate the plugin's config
                    config = load(os.path.join("plugins", plugin_name, "plugin.toml"))

                    config["metadata"]["name"] = plugin_name

                    # Return early if `live` is false
                    if not config["metadata"].get("live", True):
                        plugin = self.plugin_service.get_plugin_by_name(plugin_name)
                        if plugin:
                            self.plugin_service.delete_plugin(plugin)
                        print(
                            f"Plugin {plugin_name} has `live` set to `false`; skipping."
                        )
                        return

                    try:
                        validated_config = PluginConfig(**config)
                    except ValidationError as e:
                        print(f"Invalid configuration for plugin {plugin_name}: {e}")
                        return

            if validated_config:
                # Update registry with plugin info
                self.register_plugin(
                    config=validated_config,
                    is_default=plugin_name in self.default_plugins,
                )

                # Load plugin presets
                presets_path = os.path.join("plugins", plugin_name, "presets.json")
                if os.path.exists(presets_path):
                    PresetService(self.db).load_presets(presets_path)

        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {e}")

    def register_plugin(self, config: PluginConfig, is_default: bool = False):
        print("Registering plugin", config.metadata.display_name)
        plugin = self.plugin_service.get_plugin_by_name(config.metadata.name)

        if plugin is None:
            plugin = PluginModel(name=config.metadata.name)
            plugin.is_enabled = is_default

        # Update plugin metadata
        plugin.display_name = config.metadata.display_name
        plugin.description = config.metadata.description
        plugin.icon = config.metadata.icon
        plugin.author = config.metadata.author
        plugin.url = config.metadata.url
        plugin.version = config.metadata.version

        self.db.add(plugin)

        for name, function in config.tools.items():
            self._register_function(name, function, plugin)

        for name, function in config.snippets.items():
            self._register_function(name, function, plugin)

        self.db.commit()

    def _register_function(
        self, name: str, function: Union[Tool, Snippet], plugin: PluginModel
    ):
        function_model = self.plugin_service.get_function_by_name(name)
        serialized_function = function.model_dump(exclude={"integrations"})
        serialized_settings = serialized_function.pop("settings", None)

        function_type = "tool" if isinstance(function, Tool) else "snippet"

        if function_model is None:
            function_model = FunctionModel(
                **serialized_function,
                name=name,
                type=function_type,
                settings_metadata=serialized_settings,
                plugin=plugin,
            )
            self.db.add(function_model)
        else:
            # Update the fields of the existing function instance
            for field, value in serialized_function.items():
                setattr(function_model, field, value)
            function_model.type = function_type
            function_model.settings_metadata = serialized_settings
            function_model.plugin = plugin

        function_model.integrations = []

        for integration_name in function.integrations:
            integration = IntegrationService(self.db).get_integration_by_name(
                integration_name
            )
            if integration:
                function_model.integrations.append(integration)

        self.db.commit()
