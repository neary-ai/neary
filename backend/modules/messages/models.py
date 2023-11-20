from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    Boolean,
    DateTime,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class MessageModel(Base):
    __tablename__ = "message_model"

    id = Column(Integer, primary_key=True)
    role = Column(String)
    content = Column(JSON, nullable=True)
    actions = Column(JSON, nullable=True)
    status = Column(String, nullable=True)
    function_call = Column(JSON, nullable=True)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_archived = Column(Boolean, default=False)
    conversation_id = Column(Integer, ForeignKey("conversation_model.id"))

    conversation = relationship("ConversationModel", back_populates="messages")
    bookmark = relationship("BookmarkModel", back_populates="message")


class BookmarkModel(Base):
    __tablename__ = "bookmark_model"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey("message_model.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    message = relationship("MessageModel", back_populates="bookmark")
