from datetime import datetime
import tiktoken
import pytz
import yaml

from backend.models import ConversationModel, MessageModel
from .llm_connector import LLMConnector

websocket_store = set()

class MessageHandler:
    def __init__(self, websocket=None):
        if websocket is None:
            self.websocket = next(iter(websocket_store), None)
        else:
            self.websocket = websocket

    async def send_alert_to_ui(self, message, conversation_id):
        if self.websocket:
            await self.websocket.send_json({'role': 'alert', 'content': message, 'conversation_id': conversation_id, 'status': None})
        else:
            print('No websocket available!')

    async def send_command_to_ui(self, message, conversation_id):
        if self.websocket:
            await self.websocket.send_json({'role': 'command', 'content': message, 'conversation_id': conversation_id, 'status': None})
        else:
            print('No websocket available!')

    async def send_message_to_ui(self, message, conversation_id):
        if self.websocket:
            await self.websocket.send_json({"role": "assistant", "content": message, "conversation_id": conversation_id, 'status': None})
        else:
            print('No websocket available!')

    async def send_notification_to_ui(self, notification, conversation_id, actions=None, flash=False, save_to_db=True):
        
        message_data = {"role": "notification", "content": notification, "conversation_id": conversation_id, "actions": actions, 'status': None}
        
        if save_to_db:
            message = await self.save_message(message_data)
            message_data = message.serialize()
        if self.websocket:
            await self.websocket.send_json(message_data)
        else:
            print('No websocket available!')

    async def get_ai_response(self, context, api_type, model, streaming=True):
        '''Queries the LLM and streams the response to the UI'''
        self.log_message_history(context)

        if self.websocket and streaming is True:
            websocket = self.websocket
        else:
            websocket = None
        try:
            llm = LLMConnector(api_type=api_type, context=context, websocket=websocket)
        except Exception as e:
            await self.send_notification_to_ui(notification=str(e), conversation_id=context.conversation_id, save_to_db=False)
            return

        messages = context.get_formatted_chain()

        ai_response = await llm.create_chat(
            model=model,
            messages=messages,
            temperature=0.5
        )

        print(ai_response['content'])

        return ai_response

    def log_message_history(self, context):
        """ Save most recent message chain """
        messages = context.get_formatted_chain()
        tokenizer = tiktoken.encoding_for_model("gpt-4")
        log_file = 'data/message_history.yaml'

        total_tokens = sum(len(list(tokenizer.encode(message['content']))) for message in messages)

        now = datetime.now(pytz.timezone('US/Mountain')).strftime('%m/%d/%Y %I:%M %p')

        message_history = {
            f"New Context ({total_tokens} tokens) from {now}": [
                {message['role']: message['content']} for message in messages
            ]
        }

        with open(log_file, 'w') as f:
            yaml.dump(message_history, f, default_flow_style=False)
    
    async def save_message(self, message_data):
            message = await MessageModel.create(role=message_data['role'], content=message_data['content'], conversation_id=message_data['conversation_id'], actions=message_data.get('actions', None))
            conversation = await ConversationModel.get(id=message_data['conversation_id'])
            conversation.updated_at = datetime.utcnow()
            await conversation.save()
            return message