import json
import typing

from fastapi import WebSocket, WebSocketDisconnect
from database import SessionLocal

from modules.llms.services.llm_service import LLMFactory
from modules.conversations.models import ConversationModel
from modules.messages.services.message_service import MessageService
from modules.messages.schemas import MessageBase

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
                    message = MessageBase(**input_data)
                    yield message
                except ValueError as e:
                    print(f"Received message does not match expected format: {e}")
                    continue
            except WebSocketDisconnect:
                self.disconnect()
                break

    async def send_message_to_ui(
        self,
        message: dict,
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

    async def send_alert_to_ui(self, message: dict, type: str = None):
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

    async def send_command_to_ui(self, message: dict, conversation_id: int):
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

    async def send_status_to_ui(self, message: dict, conversation_id: int):
        print("Sending status to UI..")
        if self.websocket:
            print("With websocket: ", self.websocket)
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
        self,
        filename: str,
        filesize: str,
        file_url: str,
        conversation_id: int,
        save_to_db: bool = True,
    ):
        content = {"filename": filename, "filesize": filesize, "url": file_url}

        message_dict = {
            "role": "file",
            "content": content,
            "conversation_id": conversation_id,
            "status": None,
        }

        if save_to_db:
            MessageService(self.db).create_message(**message_dict)

        if self.websocket:
            await self.websocket.send_json(message_dict)
        else:
            print("No websocket available!")

    async def send_notification_to_ui(
        self,
        message: dict,
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

        try:
            llm = LLMFactory.create_llm(llm_settings=llm_settings, message_handler=self)
        except Exception as e:
            await self.send_notification_to_ui(
                message=str(e), conversation_id=conversation.id, save_to_db=False
            )
            return

        ai_response = await llm.create_chat(
            context=context,
            conversation_id=conversation.id,
            functions=functions,
            stream=streaming,
        )

        return ai_response
