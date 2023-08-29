import tiktoken

from backend.models.models import ConversationModel


class ContextManager:
    def __init__(self, conversation):
        self.conversation = conversation
        self.token_limit = conversation.settings['token_limit']

    async def generate_context(self, messages):
        conversation_model = await ConversationModel.get_or_none(id=self.conversation.id)
        conversation_messages = await conversation_model.messages

        conversation_history = [message.serialize(
        ) for message in conversation_messages if not message.is_archived]
        sorted_history = sorted(conversation_history,
                                key=lambda x: x['id'], reverse=True)

        messages = self.get_truncated_context(sorted_history, messages)

        return messages

    """
    Context generators
    """

    def get_truncated_context(self, sorted_history, messages):
        tokenizer = tiktoken.encoding_for_model("gpt-4")
        token_count = 0

        for message in messages.get_chain():
            tokens = len(list(tokenizer.encode(message.content)))
            message.tokens = tokens
            token_count += tokens

        # Insert context messages before we append the user's message
        insert_index = len(messages.get_precompiled_chain())

        for message in sorted_history:
            if not message['content']:
                continue

            new_message_tokens = len(
                list(tokenizer.encode(message['content'])))

            if token_count + new_message_tokens > self.token_limit:
                break

            if message['role'] == 'user' or message['role'] == 'tool':
                messages.add_user_message(
                    message['content'], id=message['id'], tokens=new_message_tokens, index=insert_index)
            elif message['role'] == 'assistant':
                messages.add_ai_message(
                    message['content'], id=message['id'], tokens=new_message_tokens, index=insert_index)
            elif message['role'] == 'system':
                messages.add_system_message(
                    message['content'], id=message['id'], tokens=new_message_tokens, index=1)
            else:
                continue

            token_count += new_message_tokens

        print(f'Final request: {token_count} tokens.')
