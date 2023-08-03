from datetime import datetime
import tiktoken

from .messages import MessageChain
from .models.models import ConversationModel, MessageModel, SpaceModel

class BaseMemory:
    def __init__(self, program):
        self.program = program
        self.token_limit = 4000
        self.memory_mode = "truncate"
        self.sticky_messages = []

        if self.program.memory_config:
            self.apply_config(self.program.memory_config)

    def apply_config(self, memory_config):
        for key, value in memory_config.items():
            if hasattr(self, key):
                setattr(self, key, value)

    async def generate_context(self, messages):
        if not messages.conversation_id:
            print('A conversation ID is required to generate context!')
            return None
        
        conversation_model = await ConversationModel.get_or_none(id=messages.conversation_id)
        conversation_messages = await conversation_model.messages
        
        conversation_history = [message.serialize() for message in conversation_messages if not message.is_archived]
        sorted_history = sorted(conversation_history, key=lambda x: x['id'], reverse=True)

        if self.memory_mode == "truncate":
            messages = self.get_truncated_context(sorted_history, messages)
        
        return messages

    async def execute_memory_tasks(self, user_message, ai_response):
        pass

    """
    Context generators
    """

    def get_truncated_context(self, sorted_history, messages):
        tokenizer = tiktoken.encoding_for_model("gpt-4")
        token_count = 0

        for message in messages.get_chain():
            token_count += len(list(tokenizer.encode(message['content'])))
        
        print(f'{token_count} tokens pre-filled, now populating with truncated history.')

        # Insert context messages before we append the user's message
        insert_index = len(messages.get_precompiled_chain())
        
        for message in sorted_history:
            if not message['content']:
                continue

            new_message_tokens = len(list(tokenizer.encode(message['content'])))

            if token_count + new_message_tokens > self.token_limit:
                break
            
            if message['role'] == 'user' or message['role'] == 'tool':
                messages.user_msg(message['content'], index=insert_index)
            elif message['role'] == 'assistant':
                messages.ai_msg(message['content'], index=insert_index)
            elif message['role'] == 'system':
                messages.system_msg(message['content'], index=1)
            else:
                continue

            token_count += new_message_tokens
        
        print(f'Final request: {token_count} tokens.')
        
        return messages

    """
    Database utility methods
    """

    async def new_conversation(self, space: SpaceModel):
        new_conversation = await ConversationModel.create(space=space)
        message = MessageModel(role="system", content=self.system_message, conversation=new_conversation)
        await message.save()
        return new_conversation

    async def get_recent_conversation(self, space: SpaceModel = None):
        if space:
            recent_conversation = await ConversationModel.filter(space=space, is_archived=False).order_by("-id").first()
        else:
            recent_conversation = await ConversationModel.filter(is_archived=False).order_by("-id").first()
        return recent_conversation

    async def save_message(self, message_data):
        if message_data['content'] and type(message_data['content']) == str:
            await MessageModel.create(role=message_data['role'], content=message_data['content'], conversation_id=message_data['conversation_id'], actions=message_data.get('actions', None), metadata=message_data.get('metadata', None))
            conversation = await ConversationModel.get(id=message_data['conversation_id'])
            conversation.updated_at = datetime.utcnow()
            await conversation.save()