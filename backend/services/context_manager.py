import tiktoken

from backend.database import SessionLocal
from backend.services import conversation_service


class ContextManager:
    def __init__(self, conversation):
        self.conversation = conversation
        self.max_input_tokens = conversation.settings['max_input_tokens']

    def generate_context(self, messages):
        conversation_model = conversation_service.get_conversation_by_id(SessionLocal(), self.conversation.id)
        conversation_messages = conversation_model.messages

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
            if not message['content'] and len(message['metadata']) == 0:
                continue

            new_message_tokens = len(
                list(tokenizer.encode(message['content'])))

            if token_count + new_message_tokens > self.max_input_tokens:
                break

            if message['role'] == 'user':
                messages.add_user_message(
                    message['content'], id=message['id'], tokens=new_message_tokens, index=insert_index)
            elif message['role'] == 'assistant':
                function_call = None
                if message['metadata']:
                    function_call = next((item['function_call'] for item in message['metadata'] if 'function_call' in item), None)
                messages.add_ai_message(message['content'], function_call=function_call, id=message['id'], tokens=new_message_tokens, index=insert_index)
            elif message['role'] == 'function':
                function_name = next((item['function_name'] for item in message['metadata'] if 'function_name' in item), None)
                messages.add_function_message(message['content'], name=function_name, id=message['id'], tokens=new_message_tokens, index=insert_index)
            elif message['role'] == 'system':
                messages.add_system_message(
                    message['content'], id=message['id'], tokens=new_message_tokens, index=1)
            else:
                continue

            token_count += new_message_tokens

        print(f'Final request: {token_count} tokens.')
