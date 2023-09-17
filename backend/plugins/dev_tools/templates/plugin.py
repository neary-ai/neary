from backend.config import settings
from backend.services import UserProfileManager, MessageHandler, CredentialManager, FileManager
from backend.plugins import BasePlugin, snippet, tool


class PluginClassName(BasePlugin):
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

    @snippet
    async def example_snippet(self, context):
        context.add_snippet("Snippet text goes here")

    @tool
    async def example_tool(self, arg1: int, arg2: int = 0) -> int:
        tool_output = arg1 + arg2
        return tool_output