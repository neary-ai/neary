from backend.plugins import Snippet
from backend.services import DocumentManager

class DocumentSnippet(Snippet):
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)
        self.document_manager = DocumentManager(conversation.id)

    async def run(self, context):
        max_results = self.settings['results']

        query = context.get_user_message()

        if query:
            document_data = []
            context_docs = await self.document_manager.similar_search(query)
            context_str = "The following document snippets have been provided as context to this conversation, reference as needed:\n\n"

            for doc in context_docs[:max_results]:
                context_str += "*" * 30 + '\n' + \
                    doc['content'] + "*" * 30 + '\n'
                document_data.append(
                    {'source': doc['source'], 'content': doc['content'], 'score': doc['similarity_score']})

            # Append relevant document snippets as context
            context.add_snippet(context_str)

            # Add sources metadata to display on the frontend
            context.add_metadata({'documents': document_data})