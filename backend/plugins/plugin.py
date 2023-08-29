import os
import toml
import inspect
from abc import ABC, abstractmethod

from backend.models import PluginInstanceModel


class Plugin(ABC):

    is_internal = False
    
    def __init__(self, id, conversation, settings=None, data=None):
        self.id = id
        self.conversation = conversation
        self.settings, self.metadata = self.load_config()
        if settings is not None:
            self.settings.update(settings)
        self.data = {} if data is None else data

    def load_config(self):
        # Load the default settings & metadata from the TOML file
        config_path = os.path.join(os.path.dirname(inspect.getfile(self.__class__)), "plugin.toml")
        config = toml.load(config_path)
        return config.get("settings", {}), config.get("metadata", {})

    async def save_state(self):
        plugin_instance = await PluginInstanceModel.get(id=self.id)
        plugin_instance.settings = self.settings
        plugin_instance.data = self.data
        await plugin_instance.save()

    def get_plugin_data(self, plugin_name):
        return self.conversation.get_plugin_data(plugin_name)

    @abstractmethod
    async def run(self, *args, **kwargs):
        pass
