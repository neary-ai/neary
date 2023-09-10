from fastapi import HTTPException, status, Request, APIRouter, Body
from fastapi.responses import JSONResponse

from backend.models import *

router = APIRouter()

@router.post("")
async def create_space(name: str = Body(...)):
    """Create a new space"""
    space = await SpaceModel.create(name=name)

    return await space.serialize()


@router.get("")
async def get_spaces(request: Request):
    """Get spaces"""
    spaces = await SpaceModel.filter(is_archived=False)

    serialized_spaces = []

    for space in spaces:
        serialized_space = await space.serialize()
        serialized_spaces.append(serialized_space)

    return serialized_spaces


@router.put("/{space_id}")
async def update_space(space_id: int, name: str = Body(...)):
    """Update a space"""
    space = await SpaceModel.get(id=space_id)

    if not space:
        return JSONResponse(status_code=404, content={"detail": "Space not found."})

    space.name = name
    await space.save()

    return JSONResponse(status_code=200, content={"detail": "Space name updated"})


@router.patch("/{space_id}")
async def archive_space(space_id: int):
    """Archive a space"""
    space = await SpaceModel.get_or_none(id=space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")

    space.is_archived = True
    await space.save()

    conversations = await ConversationModel.filter(space_id=space_id)
    
    for conversation in conversations:
        conversation.space_id = None
        await conversation.save()

    return {"detail": "Space archived"}
