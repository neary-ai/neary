from backend.plugins import Tool
from backend.services import DocumentManager


class LoadUrlsTool(Tool):
    name = "load_urls"
    display_name = "Load URLs"
    description = "Creates documents from webpages of your choosing."
    llm_description = "`load_urls`: Loads the content from a list of URLs into memory for analysis. Takes a `urls` (list) argument."

    requires_approval = True
    follow_up_on_output = True

    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

    async def run(self, urls):
        document_manager = DocumentManager(self.conversation.id)

        try:
            await document_manager.load_urls(urls)
            return "The URLs were parsed and loaded!"
        except:
            return "There was an error while trying to parse and load the URLs."
