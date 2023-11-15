from typing import Optional, List

from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request, APIRouter, Depends, Body
from fastapi.responses import JSONResponse, FileResponse

from database import get_db
from .schemas import *
from .models import *
from modules.messages.schemas import MessageBase
from modules.messages.services.message_service import MessageService
from modules.approvals.services.approval_service import ApprovalService
from modules.presets.services.preset_service import PresetService
from .services.conversation_service import ConversationService

router = APIRouter()


@router.get("/conversations", response_model=List[Conversation])
def get_conversations(db: Session = Depends(get_db)):
    service = ConversationService(db)
    conversations = service.get_conversations()

    if conversations is None:
        raise HTTPException(status_code=400, detail="Conversations couldn't be fetched")

    return conversations


@router.post("/conversations", response_model=Conversation)
def create_conversation(
    conversation: ConversationCreate, db: Session = Depends(get_db)
):
    service = ConversationService(db)
    db_conversation = service.create_conversation(
        title=conversation.title,
        space_id=conversation.space_id,
        preset_id=conversation.preset_id,
    )

    if db_conversation is None:
        raise HTTPException(status_code=400, detail="Conversation could not be created")

    return db_conversation


@router.get("/conversations/settings")
async def get_settings_options():
    # TO-DO: Move these to config file
    options = {
        "llm": {
            "api_type": [
                {
                    "option": "OpenAI",
                    "value": "openai",
                },
                {
                    "option": "Azure",
                    "value": "azure",
                },
                {
                    "option": "Custom",
                    "value": "custom",
                },
            ],
            "model": [
                {"option": "gpt-4", "value": "gpt-4"},
                {"option": "gpt-4-turbo", "value": "gpt-4-1106-preview"},
                # {"option": "gpt-4-vision", "value": "gpt-4-vision-preview"},
                {"option": "gpt-3.5-turbo", "value": "gpt-3.5-turbo"},
            ],
        }
    }

    return options


@router.patch("/conversations/{conversation_id}")
async def archive_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Archive a conversation"""

    conversation = ConversationService(db).get_conversation_by_id(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )

    ConversationService(db).archive_conversation(conversation)

    return {"detail": "Conversation archived"}


@router.put("/conversations/{conversation_id}", response_model=Conversation)
async def update_conversation(
    request: Request, conversation_id: int, db: Session = Depends(get_db)
):
    """Update a conversation's settings"""
    conversation_data = await request.json()

    conversation = ConversationService(db).get_conversation_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    updated_conversation = ConversationService(db).update_conversation(
        conversation, conversation_data
    )

    return updated_conversation


@router.post("/conversations/{conversation_id}/preset", response_model=Conversation)
async def set_conversation_preset(
    conversation_id: int, preset_id: int = Body(...), db: Session = Depends(get_db)
):
    """Update a conversation's preset"""

    conversation = ConversationService(db).get_conversation_by_id(conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    updated_conversation = PresetService(db).apply_preset(conversation, preset_id)

    return updated_conversation


@router.post("/conversations/{conversation_id}/function", response_model=Conversation)
async def add_conversation_function(
    conversation_id: int,
    function_name: str = Body(...),
    plugin_name: str = Body(...),
    db: Session = Depends(get_db),
):
    """Add a function (tool/snippet) to a conversation"""
    conversation = ConversationService(db).get_conversation_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    updated_conversation = ConversationService(db).add_conversation_function(
        function_name=function_name, plugin_name=plugin_name, conversation=conversation
    )

    return updated_conversation


@router.delete("/conversations/{conversation_id}/function", response_model=Conversation)
async def remove_conversation_function(
    conversation_id: int,
    function_name: str,
    db: Session = Depends(get_db),
):
    """Remove a function (tool/snippet) from a conversation"""
    conversation = ConversationService(db).get_conversation_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    updated_conversation = ConversationService(db).remove_conversation_function(
        function_name=function_name, conversation=conversation
    )

    return updated_conversation


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: int,
    archived: Optional[bool] = False,
    db: Session = Depends(get_db),
):
    """Get a conversation's messages"""
    conversation = ConversationService(db).get_conversation_by_id(conversation_id)
    if conversation:
        if archived:
            messages = conversation.messages
        else:
            messages = [
                message for message in conversation.messages if not message.is_archived
            ]
        serialized_messages = [
            MessageBase.model_validate(message).model_dump() for message in messages
        ]
        return {"messages": serialized_messages}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.post("/conversations/{conversation_id}/messages/archive")
async def archive_conversation_messages(
    conversation_id: int, db: Session = Depends(get_db)
):
    """Archive a conversation's messages"""
    conversation = ConversationService(db).get_conversation_by_id(conversation_id)
    if conversation:
        for message in conversation.messages:
            MessageService(db).archive_message(message)
        return JSONResponse(content={"status": "success"})
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.get("/conversations/{conversation_id}/export")
async def export_conversation_data(
    conversation_id: int, export_format: str = "txt", db: Session = Depends(get_db)
):
    """Export a conversation's messages in plain text or JSON format"""
    file_name = ConversationService(db).export_conversation(
        conversation_id, export_format
    )
    return FileResponse(
        file_name, media_type="application/octet-stream", filename=file_name
    )
