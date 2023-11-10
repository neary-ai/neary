import json
import typing

from fastapi import WebSocket, WebSocketDisconnect
from database import SessionLocal

from modules.conversations.services.llm_connector import LLMConnector
from modules.conversations.models import ConversationModel
from modules.messages.services.message_service import MessageService
from modules.messages.schemas import UserMessage

if typing.TYPE_CHECKING:
    from modules.messages.services.message_chain import MessageChain

websocket_store = set()


class MessageHandler:
    def __init__(self, websocket: WebSocket = None, db: SessionLocal = None):
        if websocket:
            websocket_store.add(websocket)

        self.websocket = websocket if websocket else next(iter(websocket_store), None)
        self.db = db if db else SessionLocal()

    def disconnect(self):
        websocket_store.remove(self.websocket)
        self.websocket = next(iter(websocket_store), None)

    async def receive_messages(self):
        """
        Continuously receive and validate messages from the frontend
        """
        while True:
            try:
                input_data = await self.websocket.receive_json()
                try:
                    user_message = UserMessage(**input_data)
                    yield user_message
                except ValueError as e:
                    print(f"Received message does not match expected format: {e}")
                    continue
            except WebSocketDisconnect:
                self.disconnect()
                break

    async def send_message_to_ui(
        self,
        message: str,
        conversation_id: int,
        metadata: list = None,
        xray: dict = None,
        function_call: dict = None,
        status: str = None,
        save_to_db: bool = True,
    ):
        message_dict = {
            "role": "assistant",
            "content": message,
            "conversation_id": conversation_id,
            "metadata": metadata,
            "xray": xray,
            "function_call": function_call,
            "status": status,
        }

        if save_to_db:
            MessageService(self.db).create_message(**message_dict)

        if self.websocket:
            await self.websocket.send_json(message_dict)
        else:
            print("No websocket available!")

    async def send_alert_to_ui(self, message: str, type: str = None):
        if self.websocket:
            await self.websocket.send_json(
                {
                    "role": "alert",
                    "content": message,
                    "type": type,
                    "status": None,
                }
            )
        else:
            print("No websocket available!")

    async def send_command_to_ui(self, message: str, conversation_id: int):
        if self.websocket:
            await self.websocket.send_json(
                {
                    "role": "command",
                    "content": message,
                    "conversation_id": conversation_id,
                    "status": None,
                }
            )
        else:
            print("No websocket available!")

    async def send_status_to_ui(self, message: str, conversation_id: int):
        if self.websocket:
            await self.websocket.send_json(
                {
                    "role": "status",
                    "content": message,
                    "conversation_id": conversation_id,
                    "status": None,
                }
            )
        else:
            print("No websocket available!")

    async def send_file_to_ui(
        self, filename: str, filesize: str, file_url: str, conversation_id: int
    ):
        content = json.dumps(
            {"filename": filename, "filesize": filesize, "url": file_url}
        )
        if self.websocket:
            await self.websocket.send_json(
                {
                    "role": "file",
                    "content": content,
                    "conversation_id": conversation_id,
                    "status": None,
                }
            )
        else:
            print("No websocket available!")

    async def send_notification_to_ui(
        self,
        message: str,
        conversation_id: int,
        actions: dict = None,
        metadata: list = None,
        save_to_db: bool = False,
    ):
        message_dict = {
            "role": "notification",
            "content": message,
            "conversation_id": conversation_id,
            "actions": actions,
            "metadata": metadata,
            "status": None,
        }

        if save_to_db:
            MessageService(self.db).create_message(**message_dict)

        if self.websocket:
            await self.websocket.send_json(message_dict)
        else:
            print("No websocket available!")

    async def get_ai_response(
        self,
        conversation: ConversationModel,
        context: "MessageChain",
        functions: list = None,
        streaming: bool = True,
    ):
        """Queries the LLM and streams the response to the UI"""
        llm_settings = conversation.settings["llm"]

        if self.websocket and streaming is True:
            websocket = self.websocket
        else:
            websocket = None

        try:
            llm = LLMConnector(
                context=context,
                message_handler=self,
                api_type=llm_settings["api_type"],
            )
        except Exception as e:
            await self.send_notification_to_ui(
                message=str(e), conversation_id=conversation.id, save_to_db=False
            )
            return

        messages = context.get_formatted_chain()

        ai_response = await llm.create_chat(
            conversation_id=conversation.id,
            model=llm_settings["model"],
            max_tokens=llm_settings["max_tokens"],
            messages=messages,
            functions=functions,
            temperature=llm_settings["temperature"],
        )

        return ai_response
