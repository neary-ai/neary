from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    DateTime,
    JSON,
    Table,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

conversation_document = Table(
    "conversation_document",
    Base.metadata,
    Column("conversation_id", Integer, ForeignKey("conversation_model.id")),
    Column("document_id", Integer, ForeignKey("document_model.id")),
)


class ConversationModel(Base):
    """
    Represents a conversation within a space. Each conversation has a title,
    a link to the space it's part of, and timestamps for when it was created and last updated.
    """

    __tablename__ = "conversation_model"

    id = Column(Integer, primary_key=True)
    title = Column(String, default="New conversation")
    space_id = Column(Integer, ForeignKey("space_model.id"))
    preset_id = Column(Integer, ForeignKey("preset_model.id"), nullable=True)
    settings = Column(JSON, nullable=True)
    data = Column(JSON, nullable=True)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    space = relationship("SpaceModel", back_populates="conversations")
    preset = relationship("PresetModel", back_populates="conversations")
    messages = relationship("MessageModel", back_populates="conversation")
    plugins = relationship("PluginInstanceModel", back_populates="conversation")
    documents = relationship("DocumentModel", secondary=conversation_document)
    approval_requests = relationship(
        "ApprovalRequestModel", back_populates="conversation"
    )

    @property
    def message_ids(self):
        return [message.id for message in self.messages]

    @property
    def excerpt(self):
        if self.messages:
            last_message = self.messages[-1]
            return last_message.content
        return None
