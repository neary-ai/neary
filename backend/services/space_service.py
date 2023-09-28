from sqlalchemy.orm import Session
from backend import models

def get_active_spaces(db: Session):
    return db.query(models.SpaceModel).filter(models.SpaceModel.is_archived == False).all()

def get_space_by_id(db: Session, space_id: int):
    return db.query(models.SpaceModel).filter(models.SpaceModel.id == space_id).first()

def update_space_name(db: Session, space: models.SpaceModel, name: str):
    space.name = name
    db.commit()
    return space

def archive_space(db: Session, space: models.SpaceModel):
    space.is_archived = True
    db.commit()
    return space

def create_space(db: Session, name: str):
    space = models.SpaceModel(name=name)
    db.add(space)
    db.commit()
    db.refresh(space)
    return space