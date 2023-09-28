from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship

from .base import Base

class SpaceModel(Base):
    """
    Represents a unique space, which is a container for conversations.
    """
    __tablename__ = 'space_model'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text, nullable=True)
    is_archived = Column(Boolean, default=False)

    # This establishes a one-to-many relationship with the ConversationModel
    conversations = relationship("ConversationModel", back_populates="space")

    def __str__(self):
        return self.name

    def serialize(self):
        conversation_ids = [conversation.id for conversation in self.conversations if not conversation.is_archived]

        space_data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "conversations": conversation_ids,
            "is_archived": self.is_archived
        }

        return space_data