from pydantic import BaseModel


class ChatModel(BaseModel):
    api: str
    model: str