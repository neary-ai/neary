from sqlalchemy.orm import Session

from ..models import SpaceModel


class SpaceService:
    def __init__(self, db: Session):
        self.db = db

    def create_space(self, name: str):
        space = SpaceModel(name=name)
        self.db.add(space)
        self.db.commit()
        self.db.refresh(space)
        return space

    def get_spaces(self):
        return self.db.query(SpaceModel).filter(SpaceModel.is_archived == False).all()

    def get_space_by_id(self, space_id: int):
        return self.db.query(SpaceModel).filter(SpaceModel.id == space_id).first()

    def update_space_name(self, space: SpaceModel, name: str):
        if name is not None:
            space.name = name
        self.db.commit()
        self.db.refresh(space)
        return space

    def archive_space(self, space: SpaceModel):
        space.is_archived = True
        self.db.commit()
        self.db.refresh(space)
        return space

    def get_space_options(self):
        spaces = self.get_spaces()
        space_options = [{"option": space.name, "value": space.id} for space in spaces]

        return space_options
