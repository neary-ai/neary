from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.services.message_handler import MessageHandler

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint"""
    await websocket.accept()

    message_handler = MessageHandler(websocket)

    try:
        await message_handler.receive_message()
    except WebSocketDisconnect:
        await message_handler.disconnect()