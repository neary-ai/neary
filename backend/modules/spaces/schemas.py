from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class Space(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    is_archived: bool
    conversation_ids: Optional[List[int]]


class SpaceCreate(BaseModel):
    name: str


class SpaceUpdate(BaseModel):
    name: Optional[str] = None
