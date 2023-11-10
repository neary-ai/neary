from pathlib import Path

from sqlalchemy.orm import Session
from fastapi import (
    HTTPException,
    Request,
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Depends,
)
from fastapi.responses import JSONResponse, FileResponse

from database import get_db
from .schemas import InitialData
from users.services import UserService
from core.services.message_handler import MessageHandler
from modules.conversations.services.chat_service import ChatService

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint"""
    await websocket.accept()

    message_handler = MessageHandler(websocket)

    async for user_message in message_handler.receive_messages():
        chat_service = ChatService(
            db=message_handler.db, message_handler=message_handler
        )
        await chat_service.handle_message(
            conversation_id=user_message.conversation_id, user_message=user_message
        )


@router.get("/files/{conversation_id}/{filename}")
async def serve_file(conversation_id: int, filename: str):
    base_directory = Path(__file__).resolve().parent.parent.parent / "data" / "files"
    file_path = base_directory / str(conversation_id) / filename
    return FileResponse(
        str(file_path),
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/api/initialize", response_model=InitialData)
async def get_initial_data(db: Session = Depends(get_db)):
    from .services.core_service import InitService

    initial_data = InitService(db).initialize_app()

    if initial_data is None:
        raise HTTPException(status_code=400, detail="Couldn't retrieve initial data")

    return initial_data


@router.get("/api/state")
async def get_state(db: Session = Depends(get_db)):
    """Get app state & initial data"""
    try:
        state_data = UserService(db).get_state()
        return state_data
    except:
        return None


@router.post("/api/state")
async def save_state(request: Request, db: Session = Depends(get_db)):
    """Save app state"""
    state_data = await request.json()
    UserService(db).update_app_state(state_data)
    return JSONResponse(status_code=200, content={"detail": "success"})
