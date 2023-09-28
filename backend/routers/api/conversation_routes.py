from typing import Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request, APIRouter, Body, Depends
from fastapi.responses import JSONResponse,  FileResponse

from backend.models import *
from backend.database import get_db
from backend.services import conversation_service, message_service
from backend.utils.utils import export_conversation

router = APIRouter()

@router.get("")
async def get_conversations(space_id: int = Body(...), db: Session = Depends(get_db)):
    """Get conversations"""
    conversations = conversation_service.get_conversations(db, space_id)
    serialized_conversations = [conversation.serialize() for conversation in conversations]

    return serialized_conversations

@router.post("")
async def create_conversation(request: Request, db: Session = Depends(get_db)):
    """Create a conversation"""
    data = await request.json()
    space_id = data['space_id']
    plugins = data.get('plugins', [])

    conversation = conversation_service.create_conversation_and_plugins(db, space_id, plugins)

    return conversation.serialize()

@router.get("/settings")
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
                {
                    "option": "gpt-4",
                    "value": "gpt-4"
                },
                {
                    "option": "gpt-3.5-turbo",
                    "value": "gpt-3.5-turbo"
                },
            ]
        }
    }

    return options

@router.get("/{conversation_id}")
async def get_conversation(conversation_id: int = None, db: Session = Depends(get_db)):
    """Get a single conversation"""
    conversation = conversation_service.get_conversation_by_id(db, conversation_id)
    if conversation:
        return conversation.serialize()
    else:
        print('Conversation not found!')


@router.patch("/{conversation_id}")
async def archive_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Archive a conversation"""

    conversation = conversation_service.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Conversation not found")

    conversation_service.archive_conversation(conversation)
    
    return {"detail": "Conversation archived"}


@router.put("/{conversation_id}")
async def update_conversation(request: Request, conversation_id: int, db: Session = Depends(get_db)):
    """Update a conversation's settings"""
    conversation_data = await request.json()

    conversation = conversation_service.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation_service.update_conversation(db, conversation, conversation_data)

    space_id = conversation_data.get('space_id')
    conversation_service.update_conversation_space(db, conversation, space_id)
 
    preset_data = conversation_data.get('preset')
    conversation_service.update_conversation_preset(db, conversation, preset_data)

    new_plugin_data = conversation_data.get('plugins', [])
    conversation_service.update_conversation_plugins(db, conversation, new_plugin_data)

    return conversation.serialize()


@router.get("/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: int, archived: Optional[bool] = False, db: Session = Depends(get_db)):
    """Get a conversation's messages"""
    conversation = conversation_service.get_conversation_by_id(db, conversation_id)
    if conversation:
        if archived:
            messages = conversation.messages
        else:
            messages = [message for message in conversation.messages if not message.is_archived]
        serialized_messages = [message.serialize() for message in messages]
        return {"messages": serialized_messages}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.post("/{conversation_id}/messages/archive")
async def archive_conversation_messages(conversation_id: int, db: Session = Depends(get_db)):
    """Archive a conversation's messages"""
    conversation = conversation_service.get_conversation_by_id(db, conversation_id)
    if conversation:
        for message in conversation.messages:
            message_service.archive_message(db, message)
        return JSONResponse(content={"status": "success"})
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.get("/{conversation_id}/export")
async def export_conversation_data(conversation_id: int, 
                                   export_format: str = 'txt', 
                                   db: Session = Depends(get_db)):
    """Export a conversation's messages in plain text or JSON format"""
    file_name = export_conversation(db, conversation_id, export_format)
    return FileResponse(file_name, media_type="application/octet-stream", filename=file_name)