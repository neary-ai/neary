from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    role: str
    conversation_id: Optional[int] = None
    content: str
    function_call: Optional[dict] = None
    metadata: Optional[list] = Field(None, alias="meta_data")
    tokens: Optional[int] = None
    actions: Optional[list] = None
    created_at: Optional[datetime] = None
    is_archived: Optional[bool] = None


class NotificationMessage(MessageBase):
    role: str = "notification"


class UserMessage(MessageBase):
    role: str = "user"


class SystemMessage(MessageBase):
    role: str = "system"


class SnippetMessage(MessageBase):
    role: str = "snippet"


class FunctionMessage(MessageBase):
    role: str = "function"


class AssistantMessage(MessageBase):
    role: str = "assistant"
    content: Optional[str] = None
    status: Optional[str] = None
    xray: Optional[dict] = None
