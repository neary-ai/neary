from backend.plugins import BasePlugin, snippet, tool
from modules.documents.services.document_service import DocumentManager


class DocumentSearch(BasePlugin):
    def __init__(self, id, conversation_id, services, settings=None, data=None):
        super().__init__(id, conversation_id, services, settings, data)
        self.document_manager = DocumentManager(conversation_id)

    @snippet
    async def insert_similar_documents(self, context):
        max_results = self.settings["insert_similar_documents"]["max_results"]

        query = context.get_user_message()

        if query:
            document_data = []
            context_docs = await self.document_manager.similar_search(query)
            context_str = "The following document snippets have been provided as context to this conversation, reference as needed:\n\n"

            for doc in context_docs[:max_results]:
                context_str += "*" * 30 + "\n" + doc["content"] + "*" * 30 + "\n"
                document_data.append(
                    {
                        "source": doc["source"],
                        "content": doc["content"],
                        "score": doc["similarity_score"],
                    }
                )

            # Append relevant document snippets as context
            context.add_snippet(context_str)

            # Add sources metadata to display on the frontend
            context.add_metadata({"documents": document_data})

    @tool
    async def load_url(self, url):
        document_manager = DocumentManager(self.conversation_id)

        try:
            await document_manager.load_url(url)
            return "The URL was parsed and loaded!"
        except:
            return "There was an error while trying to parse and load the URL."
