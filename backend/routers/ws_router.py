from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.conversation import Conversation
from backend.models import ConversationModel
from backend.services.message_handler import MessageHandler, websocket_store

router = APIRouter()

async def process_input(user_message, message_handler):
    """
    Entry point for user messages from the frontend
    """
    conversation_model = await ConversationModel.get_or_none(id=user_message['conversation_id'])    
    conversation_data = await conversation_model.serialize() if conversation_model else None
    conversation = await Conversation.from_json(conversation_data, message_handler) if conversation_data else None

    if conversation:
        await conversation.handle_message(user_message)
    else:
        print('No conversation found!')
        return

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint"""
    await websocket.accept()
    websocket_store.add(websocket)
    message_handler = MessageHandler(websocket)

    try:
        while True:
            try:
                input_data = await websocket.receive_json()
                await process_input(input_data, message_handler)
            except WebSocketDisconnect:
                break

    finally:
        websocket_store.remove(websocket)
        websocket = None