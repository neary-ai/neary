from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from database import Base


class SpaceModel(Base):
    """
    Represents a unique space, which is a container for conversations.
    """

    __tablename__ = "space_model"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    is_archived = Column(Boolean, default=False)

    conversations = relationship("ConversationModel", back_populates="space")

    @hybrid_property
    def conversation_ids(self):
        return [conversation.id for conversation in self.conversations]
