from typing import Optional, List

from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request, APIRouter, Depends
from fastapi.responses import JSONResponse, FileResponse

from database import get_db
from .schemas import *
from .models import *
from .services import MessageService

router = APIRouter()

@router.patch("/messages/{message_id}")
async def archive_message(message_id: int, db: Session = Depends(get_db)):
    """Archive a message"""

    message = await MessageModel.get_or_none(id=message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
        )

    message.is_archived = True
    await message.save()
    return {"detail": "Message archived"}