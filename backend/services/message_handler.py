import json

from backend.conversation import Conversation
from backend.schemas import UserMessage
from backend.services import conversation_service, message_service
from .llm_connector import LLMConnector
from backend.database import SessionLocal

websocket_store = set()

class MessageHandler:
    def __init__(self, websocket=None, db=None):
        if websocket is None:
            self.websocket = next(iter(websocket_store), None)
        else:
            self.websocket = websocket
        websocket_store.add(self.websocket)

        self.db = db if db else SessionLocal()

    async def disconnect(self):
        websocket_store.remove(self.websocket)
        self.websocket = None

    async def receive_message(self):
        """
        Receive message from the frontend and process it
        """
        while True:
            input_data = await self.websocket.receive_json()

            try:
                user_message = UserMessage(**input_data)
            except ValueError as e:
                print(f"Received message does not match expected format: {e}")
                continue

            conversation_model = conversation_service.get_conversation_by_id(self.db, user_message.conversation_id)
            
            serialized = conversation_model.serialize()

            conversation = Conversation(id=serialized['id'], 
                                        title=serialized['title'], 
                                        settings=serialized['settings'], 
                                        plugins=serialized['plugins'], 
                                        message_handler=self)

            conversation.load_plugins()
            
            await conversation.handle_message(user_message.content)


    async def send_message_to_ui(self, message, conversation_id, save_to_db=True):
        if save_to_db:
            message = message_service.create_message(self.db, role="assistant", content=message, conversation_id=conversation_id)
            message_data = message.serialize()
        else:
            message_data = {"role": "assistant", "content": message,
                            "conversation_id": conversation_id, 'status': None}

        if self.websocket:
            await self.websocket.send_json(message_data)
        else:
            print('No websocket available!')

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
            message = message_service.create_message(self.db, role="assistant", content=message, conversation_id=conversation_id)
            message_data = message.serialize()
        else:
            message_data = {"role": "assistant", "content": message,
                            "conversation_id": conversation_id, 'status': None}

        if self.websocket:
            await self.websocket.send_json(message_data)
        else:
            print('No websocket available!')

    async def send_file_to_ui(self, filename, filesize, file_url, conversation_id, save_to_db=True):
        content = json.dumps({'filename': filename, 'filesize': filesize, 'url': file_url})
        if save_to_db:
            message = message_service.create_message(self.db, role="file", content=content, conversation_id=conversation_id)
            message_data = message.serialize()
        else:
            message_data = {"role": "file", "content": content,
                            "conversation_id": conversation_id, 'status': None}

        if self.websocket:
            await self.websocket.send_json(message_data)
        else:
            print('No websocket available!')

    async def send_notification_to_ui(self, message, conversation_id, actions=None, save_to_db=False):
        if save_to_db:
            message = message_service.create_message(self.db, role="notification", content=message, conversation_id=conversation_id, actions=actions)
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
            temperature=llm_settings['temperature'],
        )

        return ai_response
