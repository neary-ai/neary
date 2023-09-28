from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base

class MessageModel(Base):
    __tablename__ = 'message_model'

    id = Column(Integer, primary_key=True)
    role = Column(String)
    content = Column(Text)
    actions = Column(JSON, nullable=True)
    status = Column(String, nullable=True)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_archived = Column(Boolean, default=False)
    conversation_id = Column(Integer, ForeignKey('conversation_model.id'))

    # Relationship
    conversation = relationship('ConversationModel', back_populates='messages')

    def serialize(self):
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "actions": self.actions,
            "metadata": self.meta_data,
            "is_archived": self.is_archived,
            "created_at": self.created_at.isoformat(),
            "conversation_id": self.conversation_id,
        }