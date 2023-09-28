from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request, APIRouter, Body, Depends
from fastapi.responses import JSONResponse

from backend.database import get_db
from backend.services import space_service, conversation_service

router = APIRouter()

@router.post("")
async def create_space(name: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """Create a new space"""
    space = space_service.create_space(db, name)
    return space.serialize()


@router.put("/{space_id}")
async def update_space(space_id: int, name: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """Update a space"""
    space = space_service.get_space_by_id(db, space_id)

    if not space:
        return JSONResponse(status_code=404, content={"detail": "Space not found."})

    space = space_service.update_space_name(db, space, name)

    return space.serialize()


@router.patch("/{space_id}")
async def archive_space(space_id: int, db: Session = Depends(get_db)):
    """Archive a space"""
    space = space_service.get_space_by_id(db, space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")

    space = space_service.archive_space(db, space)

    conversations = conversation_service.get_conversations_by_space(db, space_id)
    
    for conversation in conversations:
        conversation_service.update_conversation_space(db, conversation, space_id=None)
    
    return space.serialize()
