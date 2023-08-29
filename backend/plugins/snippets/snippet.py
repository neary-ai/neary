from abc import abstractmethod

from ..plugin import Plugin

class Snippet(Plugin):
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

    @abstractmethod
    async def run(self, context, *args, **kwargs):
        pass