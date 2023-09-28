from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base

# Define the document association table
conversation_document = Table(
    'conversation_document',
    Base.metadata,
    Column('conversation_id', Integer, ForeignKey('conversation_model.id')),
    Column('document_id', Integer, ForeignKey('document_model.id'))
)

class ConversationModel(Base):
    """
    Represents a conversation within a space. Each conversation has a title,
    a link to the space it's part of, and timestamps for when it was created and last updated.
    """
    __tablename__ = 'conversation_model'

    id = Column(Integer, primary_key=True)
    title = Column(String, default="New conversation")
    space_id = Column(Integer, ForeignKey('space_model.id'))
    preset_id = Column(Integer, ForeignKey('preset_model.id'))
    settings = Column(JSON, nullable=True)
    data = Column(JSON, nullable=True)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    space = relationship('SpaceModel', back_populates='conversations')
    preset = relationship('PresetModel', back_populates='conversations')
    messages = relationship('MessageModel', back_populates='conversation')
    plugins = relationship('PluginInstanceModel', back_populates='conversation')
    documents = relationship('DocumentModel', secondary=conversation_document)
    approval_requests = relationship('ApprovalRequestModel', back_populates='conversation')

    def serialize(self):
        # SQLAlchemy operates synchronously, so we don't need the `async` keyword.
        # We assume here that related entities are already loaded into the session.
        recent_message = self.messages[-1].content if self.messages else None
        message_ids = [message.id for message in self.messages]

        conversation_data = {
            "id": self.id,
            "space_id": self.space_id,
            "preset": self.preset.serialize(),
            "title": self.title,
            "settings": self.settings,
            "plugins": [plugin.serialize() for plugin in self.plugins],
            "messages": message_ids,
            "excerpt": recent_message,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        return conversation_data