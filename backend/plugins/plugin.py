import os
import toml
import inspect
from abc import ABC

from backend.database import SessionLocal


class BasePlugin(ABC):
    def __init__(self, id, conversation_id, services, settings=None, data=None):
        self.id = id
        self.services = services
        self.conversation_id = conversation_id
        self.settings, self.metadata = self.load_config()

        # Simplify settings
        if settings is not None:
            for function_name, function_settings in settings.items():
                if (
                    function_name
                    and function_settings
                    and function_name in self.settings
                ):
                    for setting_key, setting_data in function_settings.items():
                        self.settings[function_name][setting_key] = setting_data[
                            "value"
                        ]

        self.data = {} if data is None else data

    def load_config(self):
        # Load the default settings & metadata from the TOML file
        config_dir = os.path.dirname(inspect.getfile(self.__class__))
        config_path = os.path.join((config_dir), "plugin.toml")
        config = toml.load(config_path)

        settings = {}
        metadata = config.get("metadata", {})
        metadata["name"] = os.path.basename(config_dir)

        # Load settings for each tool
        for tool_name, tool_config in config.get("tools", {}).items():
            tool_settings = tool_config.get("settings", {})
            for setting_name, setting_config in tool_settings.items():
                settings[tool_name] = {setting_name: setting_config.get("value", None)}

        # Load settings for each snippet
        for snippet_name, snippet_config in config.get("snippets", {}).items():
            snippet_settings = snippet_config.get("settings", {})
            for setting_name, setting_config in snippet_settings.items():
                settings[snippet_name] = {
                    setting_name: setting_config.get("value", None)
                }

        return settings, metadata

    def save_state(self):
        db = SessionLocal()
        try:
            from modules.plugins.services.plugin_service import PluginService

            PluginService(db).save_plugin_instance_state(
                self.id, self.data, self.settings
            )
        finally:
            db.close()


def snippet(func):
    func.is_snippet = True
    return func


def tool(func):
    func.is_tool = True
    return func
