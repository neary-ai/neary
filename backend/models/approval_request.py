from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from .base import Base

class ApprovalRequestModel(Base):
    __tablename__ = 'approval_request_model'

    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    conversation_id = Column(Integer, ForeignKey('conversation_model.id'))
    tool_name = Column(String)
    tool_args = Column(JSON)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    conversation = relationship('ConversationModel', back_populates='approval_requests')

    def serialize(self):
        return {
            "id": str(self.id),
            "conversation_id": self.conversation_id,
            "tool_name": self.tool_name,
            "tool_args": self.tool_args,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
