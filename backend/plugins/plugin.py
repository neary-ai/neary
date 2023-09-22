import os
import toml
import inspect
from abc import ABC

from backend.models import PluginInstanceModel
from backend.services import (
    UserProfileManager,
    CredentialManager,
    MessageHandler,
    FileManager
)

class BasePlugin(ABC):
    
    def __init__(self, id, conversation, settings=None, data=None):
        self.id = id
        self.conversation = conversation
        self.services = PluginServices(self)
        self.settings, self.metadata = self.load_config()

        # Simplify settings
        if settings is not None:
            for function_name in settings:
                if function_name in self.settings:
                    for setting_key in settings[function_name]:
                        self.settings[function_name][setting_key] = settings[function_name][setting_key]['value']

        self.data = {} if data is None else data

    def load_config(self):
        # Load the default settings & metadata from the TOML file
        config_dir = os.path.dirname(inspect.getfile(self.__class__))
        config_path = os.path.join((config_dir), "plugin.toml")
        config = toml.load(config_path)

        settings = {}
        metadata = config.get("metadata", {})
        metadata['name'] = os.path.basename(config_dir)

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
        plugin_instance.data = self.data
        
        function_instances = await plugin_instance.function_instances

        for function in function_instances:
            if function.name in self.settings:
                for setting_key in self.settings[function.name]:
                     function.settings_values[setting_key] = self.settings[function.name][setting_key]
                await function.save()

        await plugin_instance.save()

class PluginServices(FileManager, UserProfileManager, CredentialManager, MessageHandler):
    def __init__(self, plugin):
        FileManager.__init__(self, plugin)
        CredentialManager.__init__(self)
        MessageHandler.__init__(self)

def snippet(func):
    func.is_snippet = True
    return func

def tool(func):
    func.is_tool = True
    return func