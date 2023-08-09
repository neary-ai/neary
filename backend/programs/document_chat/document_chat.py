from backend.programs.tools import requires_approval
from backend.programs.scripts import parse_intent
from backend.programs.utils import get_local_time_str
from backend.messages import MessageChain
from backend.memory import BaseMemory
from ..base_program import BaseProgram

class DocumentChat(BaseProgram):

    def __init__(self, conversation):
        super().__init__(conversation)

        self.system_message = "Your job is to assist the user with document search and analysis. When provided with documents to load via a URL, you should use the `load_urls` tool. When asked a question, you should do your best to provide an answer from the provided document snippets. If there are no snippets loaded that answer the user's question, simply let them know."

        self.memory_config = {
            "memory_mode": "truncate",
            "token_limit": 3000,
        }
        self.memory = BaseMemory(self)
        
        self.register_tool("load_urls", self.load_urls)
        
        self.toolbox = ['update_profile', 'make_a_note', 'clear_notes', 'load_urls']

    async def execute(self, user_message):
        # Initialize message chain with required messages
        messages = MessageChain(system_message=self.system_message, user_message=user_message, conversation_id=user_message['conversation_id'])

        local_time_str = await get_local_time_str()
        
        if local_time_str:
            messages.user_msg(local_time_str)

        # Add avaiable tools to top of conversation
        messages.user_msg(self.get_tools_str())

        # Determine the user's intent
        intent_options = [
            "User is requesting the agent take an action, like loading a document from a URL.",
            "User is asking the agent a question which requires additional context to answer correctly.",
            "User is just chatting (no clear intent)."
        ]

        intent = parse_intent(user_message=user_message['content'], previous_message=None, options=intent_options)

        # If user is asking a question about documents, find return similar documents      
        if int(intent['answer']) == 1:
            document_data = []
            context_docs = await self.conversation.document_manager.similar_search(user_message['content'])
            context_str = "The following document snippets have been provided as context to this conversation, reference as needed:\n\n"
            
            for doc in context_docs[:3]:
                context_str += "*" * 30 + '\n' + doc['content'] + "*" * 30 + '\n'
                document_data.append({'source': doc['source'], 'content': doc['content'], 'score': doc['similarity_score']})
        
            # Append relevant document snippets as context
            messages.user_msg(context_str)
            
            # Add sources metadata to display on the frontend
            messages.add_metadata({'documents': document_data})
        
        # Use remaining tokens to provide context prior messages in the conversation
        context = await self.memory.generate_context(messages)

        ai_response = await self.conversation.message_handler.get_ai_response(context, self.api_type, self.model)

        await self.memory.save_message(user_message)
        await self.memory.save_message(ai_response)

        await self.handle_tool_requests(ai_response)

        return ai_response


    @requires_approval
    async def load_urls(self, urls):
        """
        "load_urls": Loads the content from a list of URLs into memory for analysis. Takes a `urls` (list) argument.
        """
        try:
            result = await self.conversation.document_manager.load_urls(urls)
            return True
        except:
            return False