from pathlib import Path

from sqlalchemy.orm import Session
from fastapi import (
    HTTPException,
    Request,
    APIRouter,
    WebSocket,
    Depends,
)
from fastapi.responses import JSONResponse, FileResponse

from database import get_db
from .schemas import InitialData
from users.services import UserService
from core.services.message_handler import MessageHandler
from modules.conversations.services.chat_service import ChatService
from modules.approvals.services.approval_service import ApprovalService

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint"""
    await websocket.accept()

    message_handler = MessageHandler(websocket)

    async for message in message_handler.receive_messages():
        if message.role == "user":
            chat_service = ChatService(
                db=message_handler.db, message_handler=message_handler
            )
            await chat_service.handle_message(
                conversation_id=message.conversation_id, user_message=message
            )
        elif message.role == "action":
            approval_service = ApprovalService(
                db=message_handler.db, message_handler=message_handler
            )
            await approval_service.handle_approval_response(
                data=message.content.data,
                message_id=message.content.message_id,
            )


@router.get("/api/files/{conversation_id}/{filename}")
async def serve_file(conversation_id: int, filename: str):
    base_directory = Path(__file__).resolve().parent.parent / "data" / "files"
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
