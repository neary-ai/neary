from ..plugin import Plugin

class Tool(Plugin):
    
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)