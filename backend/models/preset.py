from sqlalchemy import Column, Integer, String, Text, Boolean, JSON
from sqlalchemy.orm import relationship

from .base import Base

class PresetModel(Base):
    __tablename__ = 'preset_model'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    plugins = Column(JSON, nullable=True)
    settings = Column(JSON, nullable=True)
    is_default = Column(Boolean, default=False)
    is_custom = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Relationship
    conversations = relationship('ConversationModel', back_populates='preset')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "plugins": self.plugins,
            "settings": self.settings,
            "is_default": self.is_default,
            "is_custom": self.is_custom
        }
