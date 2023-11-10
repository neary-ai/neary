from sqlalchemy.orm import Session
from fastapi import HTTPException, APIRouter, Depends

from backend.database import get_db
from .schemas import *
from .services.space_service import SpaceService

router = APIRouter()


@router.post("/spaces", response_model=Space)
def create_space(space: SpaceCreate, db: Session = Depends(get_db)):
    service = SpaceService(db)
    db_space = service.create_space(name=space.name)

    if db_space is None:
        raise HTTPException(status_code=400, detail="Space could not be created")

    return db_space


@router.put("/spaces/{space_id}", response_model=Space)
def update_space(space_id: int, space: SpaceUpdate, db: Session = Depends(get_db)):
    service = SpaceService(db)
    db_space = service.get_space_by_id(space_id)
    if db_space is None:
        raise HTTPException(status_code=404, detail="Space not found")

    updated_space = service.update_space_name(db_space, space.name)
    return updated_space


@router.delete("/spaces/{space_id}", response_model=Space)
def archive_space(space_id: int, db: Session = Depends(get_db)):
    service = SpaceService(db)
    db_space = service.get_space_by_id(space_id)
    if db_space is None:
        raise HTTPException(status_code=404, detail="Space not found")

    archived_space = service.archive_space(db_space)
    return archived_space
