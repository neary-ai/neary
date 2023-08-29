from backend.plugins import Tool
from backend.services import DocumentManager

class LoadUrlTool(Tool):
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

    async def run(self, url):
        document_manager = DocumentManager(self.conversation.id)

        try:
            await document_manager.load_url(url)
            return "The URL was parsed and loaded!"
        except:
            return "There was an error while trying to parse and load the URL."