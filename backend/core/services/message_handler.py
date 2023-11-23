import json
import typing

from fastapi import WebSocket, WebSocketDisconnect
from database import SessionLocal

from modules.llms.services.llm_service import LLMFactory
from modules.conversations.models import ConversationModel
from modules.messages.services.message_service import MessageService
from modules.messages.schemas import *

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
        message: AssistantMessage,
        save_to_db: bool = True,
    ):
        message_dict = message.model_dump()

        if save_to_db:
            saved_message = MessageService(self.db).create_message(**message_dict)
            message_dict["id"] = saved_message.id

        if self.websocket:
            await self.websocket.send_json(message_dict)
        else:
            print("No websocket available!")

    async def send_alert_to_ui(self, message: AlertMessage):
        if self.websocket:
            await self.websocket.send_json(message.model_dump())
        else:
            print("No websocket available!")

    async def send_command_to_ui(self, message: CommandMessage):
        if self.websocket:
            await self.websocket.send_json(message.model_dump())
        else:
            print("No websocket available!")

    async def send_status_to_ui(self, message: StatusMessage):
        if self.websocket:
            await self.websocket.send_json(message.model_dump())
        else:
            print("No websocket available!")

    async def send_file_to_ui(
        self,
        message: FileMessage,
        save_to_db: bool = True,
    ):
        message_dict = message.model_dump()

        if save_to_db:
            saved_message = MessageService(self.db).create_message(**message_dict)
            message_dict["id"] = saved_message.id

        if self.websocket:
            await self.websocket.send_json(message_dict)
        else:
            print("No websocket available!")

    async def send_notification_to_ui(
        self,
        message: NotificationMessage,
        save_to_db: bool = False,
    ):
        message_dict = message.model_dump()

        if save_to_db:
            saved_message = MessageService(self.db).create_message(**message_dict)
            message_dict["id"] = saved_message.id

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
            message = NotificationMessage(
                message=Content(text=str(e)), conversation_id=conversation.id
            )
            await self.send_notification_to_ui(message=message, save_to_db=False)
            return

        ai_response = await llm.create_chat(
            context=context,
            conversation_id=conversation.id,
            functions=functions,
            stream=streaming,
        )

        return ai_response
