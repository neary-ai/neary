from typing import Optional, Dict, List

from pydantic import BaseModel, ConfigDict

from modules.plugins.schemas import PluginInstance


class ConversationBase(BaseModel):
    title: Optional[str] = "New conversation"
    space_id: Optional[int] = None
    preset_id: Optional[int] = None


class ConversationCreate(ConversationBase):
    pass


class Conversation(ConversationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_archived: bool
    message_ids: Optional[List[int]] = []
    excerpt: Optional[str] = None
    plugins: Optional[List[PluginInstance]] = []
    settings: Optional[Dict] = None
    data: Optional[Dict] = None


class ActionResponse(BaseModel):
    name: str
    conversation_id: int
    message_id: str | int
    data: dict
