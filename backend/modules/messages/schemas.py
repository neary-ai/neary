from enum import Enum
from typing import Optional, Dict, Union, Any, List
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, validator


class Content(BaseModel):
    text: Optional[str] = Field(None)

    class Config:
        extra = "allow"


class FileContent(Content):
    filename: str
    filesize: str
    file_url: str


class MessageStatusEnum(str, Enum):
    incomplete = "incomplete"
    complete = "complete"


class MessageBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    role: str
    conversation_id: Optional[int] = None
    content: Content
    function_call: Optional[dict] = None
    metadata: Optional[list] = Field(None, alias="meta_data")
    actions: Optional[list] = None
    tokens: Optional[int] = None

    status: Optional[MessageStatusEnum] = None
    created_at: Optional[datetime] = None
    is_archived: Optional[bool] = None


class AlertTypeEnum(str, Enum):
    info = "info"
    success = "success"
    error = "error"
    tool_start = "tool_start"
    tool_error = "tool_error"
    tool_success = "tool_success"


class AlertMessage(MessageBase):
    role: str = "alert"
    content: str
    type: AlertTypeEnum


class CommandMessage(MessageBase):
    role: str = "command"


class FileMessage(MessageBase):
    role: str = "file"
    content: FileContent


class StatusMessage(MessageBase):
    role: str = "status"
    content: Union[str, dict]


class NotificationMessage(MessageBase):
    role: str = "notification"


class UserMessage(MessageBase):
    role: str = "user"


class SystemMessage(MessageBase):
    role: str = "system"

    @validator("content", pre=True)
    def has_text(cls, v):
        if v.get("text") is None or v.get("text") == "":
            raise ValueError("Content must include 'text' key with non-empty value.")
        return v


class SnippetMessage(MessageBase):
    role: str = "snippet"

    @validator("content", pre=True)
    def has_text(cls, v):
        if v.get("text") is None or v.get("text") == "":
            raise ValueError("Content must include 'text' key with non-empty value.")
        return v


class FunctionMessage(MessageBase):
    role: str = "function"


class AssistantMessage(MessageBase):
    role: str = "assistant"
    xray: Optional[dict] = None


class Bookmark(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    message_id: int
    created_at: datetime


class BookmarkDetails(Bookmark):
    conversation_id: int
    message_content: Content
    conversation_title: str
