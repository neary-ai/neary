from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base


class ApprovalRequestModel(Base):
    __tablename__ = "approval_request_model"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversation_model.id"))
    tool_name = Column(String)
    tool_args = Column(JSON)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    conversation = relationship("ConversationModel", back_populates="approval_requests")
