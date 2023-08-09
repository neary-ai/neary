from backend.messages import MessageChain
from backend.memory import BaseMemory
from ..base_program import BaseProgram

class LocalChat(BaseProgram):

    def __init__(self, conversation):
        super().__init__(conversation)

        self.api_type = "local"
        self.system_message = "You are a helpful assistant."

        self.memory_config = {
            "memory_mode": "truncate",
            "token_limit": 5000,
        }
        self.memory = BaseMemory(self)
                
        self.toolbox = []

    async def execute(self, user_message):
        messages = MessageChain(system_message=self.system_message, user_message=user_message, conversation_id=user_message['conversation_id'])

        # Use remaining tokens to provide context from prior messages in the conversation
        context = await self.memory.generate_context(messages)

        ai_response = await self.conversation.message_handler.get_ai_response(context, self.api_type, self.model)

        await self.memory.save_message(user_message)
        await self.memory.save_message(ai_response)

        return ai_response