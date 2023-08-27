from ..plugin import Plugin

class Tool(Plugin):
    type = "tool"
    requires_approval = True
    follow_up_on_output = True
    
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)