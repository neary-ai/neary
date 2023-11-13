from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class Preset(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    plugins: List[dict]
    settings: dict
    is_default: bool
    is_custom: bool


class PresetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    plugins: List[dict]
    settings: dict
    is_default: bool
    is_custom: bool


class PresetFromConversation(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None


class PresetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    plugins: Optional[List[dict]] = None
    settings: Optional[dict] = None
    is_default: Optional[bool] = None
    is_custom: Optional[bool] = None


class PresetExport(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    plugins: List[dict]
    settings: dict
