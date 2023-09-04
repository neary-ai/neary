from backend.models import MessageModel
from .llm_connector import LLMConnector

websocket_store = set()


class MessageHandler:
    def __init__(self, websocket=None):
        if websocket is None:
            self.websocket = next(iter(websocket_store), None)
        else:
            self.websocket = websocket

    async def send_alert_to_ui(self, message, conversation_id, type=None):
        if self.websocket:
            await self.websocket.send_json({'role': 'alert', 'content': message, 'conversation_id': conversation_id, 'type': type, 'status': None})
        else:
            print('No websocket available!')

    async def send_command_to_ui(self, message, conversation_id):
        if self.websocket:
            await self.websocket.send_json({'role': 'command', 'content': message, 'conversation_id': conversation_id, 'status': None})
        else:
            print('No websocket available!')

    async def send_status_to_ui(self, message, conversation_id):
        if self.websocket:
            await self.websocket.send_json({'role': 'status', 'content': message, 'conversation_id': conversation_id, 'status': None})
        else:
            print('No websocket available!')

    async def send_message_to_ui(self, message, conversation_id, save_to_db=True):
        if save_to_db:
            message = await MessageModel.create(role="assistant", content=message, conversation_id=conversation_id, status=None)
            message_data = message.serialize()
        else:
            message_data = {"role": "assistant", "content": message,
                            "conversation_id": conversation_id, 'status': None}

        if self.websocket:
            await self.websocket.send_json(message_data)
        else:
            print('No websocket available!')

    async def send_notification_to_ui(self, message, conversation_id, actions=None, save_to_db=False):
        if save_to_db:
            message = await MessageModel.create(role="notification", content=message, conversation_id=conversation_id, actions=actions, status=None)
            message_data = message.serialize()
        else:
            message_data = {"role": "notification", "content": message,
                            "conversation_id": conversation_id, "actions": actions, "status": None}

        if self.websocket:
            await self.websocket.send_json(message_data)
        else:
            print('No websocket available!')

    async def get_ai_response(self, conversation, context, functions=None, streaming=True):
        '''Queries the LLM and streams the response to the UI'''
        llm_settings = conversation.settings['llm']

        if self.websocket and streaming is True:
            websocket = self.websocket
        else:
            websocket = None
        try:
            llm = LLMConnector(
                api_type=llm_settings['api_type'], context=context, websocket=websocket)
        except Exception as e:
            await self.send_notification_to_ui(message=str(e), conversation_id=conversation.id, save_to_db=False)
            return

        messages = context.get_formatted_chain()

        ai_response = await llm.create_chat(
            model=llm_settings['model'],
            max_tokens=llm_settings['max_tokens'],
            messages=messages,
            functions=functions,
            temperature=0.5,
        )

        return ai_response
