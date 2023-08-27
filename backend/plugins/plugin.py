from abc import ABC, abstractmethod

from backend.models import PluginInstanceModel


class Plugin(ABC):
    is_public = True

    def __init__(self, id, conversation, settings=None, data=None):
        self.id = id
        self.conversation = conversation
        self.settings = {} if settings is None else settings
        self.data = {} if data is None else data

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
