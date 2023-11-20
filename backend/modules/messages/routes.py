from sqlalchemy.orm import Session
from fastapi import HTTPException, status, APIRouter, Depends

from database import get_db
from .services.message_service import MessageService
from .schemas import *
from .models import *

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


@router.get("/bookmarks")
def get_all_bookmarks(db: Session = Depends(get_db)):
    message_service = MessageService(db)
    bookmarks = message_service.get_bookmarks_with_details()
    return bookmarks


@router.post("/bookmarks/{message_id}", response_model=BookmarkDetails)
def add_bookmark(message_id: int, db: Session = Depends(get_db)):
    message_service = MessageService(db)
    message = message_service.get_message_by_id(message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found."
        )
    bookmark = message_service.add_bookmark(message_id)
    return bookmark


@router.delete("/bookmarks/{message_id}")
def remove_bookmark(message_id: int, db: Session = Depends(get_db)):
    message_service = MessageService(db)
    bookmark = message_service.remove_bookmark(message_id)
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found."
        )
    return {"detail": "Bookmark removed"}
