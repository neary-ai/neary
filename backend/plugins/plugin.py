import os
import toml
import inspect
from abc import ABC

from backend.models import PluginInstanceModel


class BasePlugin(ABC):
    
    def __init__(self, id, conversation, settings=None, data=None):
        self.id = id
        self.conversation = conversation
        self.settings, self.metadata = self.load_config()

        # Simplify settings dict
        if settings is not None:
            for key in settings:
                if key in self.settings:
                    for subkey in settings[key]:
                        self.settings[key][subkey] = settings[key][subkey]['value']

        self.data = {} if data is None else data

    def load_config(self):
        # Load the default settings & metadata from the TOML file
        config_path = os.path.join(os.path.dirname(inspect.getfile(self.__class__)), "plugin.toml")
        config = toml.load(config_path)

        settings = {}
        metadata = config.get("metadata", {})

        # Load settings for each tool
        for tool_name, tool_config in config.get("tools", {}).items():
            tool_settings = tool_config.get("settings", {})
            for setting_name, setting_config in tool_settings.items():
                settings[tool_name] = {setting_name: setting_config.get("value", None)}

        # Load settings for each snippet
        for snippet_name, snippet_config in config.get("snippets", {}).items():
            snippet_settings = snippet_config.get("settings", {})
            for setting_name, setting_config in snippet_settings.items():
                settings[snippet_name] = {setting_name: setting_config.get("value", None)}

        return settings, metadata

    async def save_state(self):
        plugin_instance = await PluginInstanceModel.get(id=self.id)
        plugin_instance.settings = self.settings
        plugin_instance.data = self.data
        await plugin_instance.save()

def snippet(func):
    func.is_snippet = True
    return func

def tool(func):
    func.is_tool = True
    return func