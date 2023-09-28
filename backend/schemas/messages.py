from pydantic import BaseModel
from enum import Enum

class RoleEnum(str, Enum):
    assistant = "assistant"
    user = "user"

class UserMessage(BaseModel):
    role: RoleEnum
    conversation_id: int
    content: str