from sqlalchemy import Column, Integer, String, Text, Boolean, JSON
from sqlalchemy.orm import relationship

from .base import Base

class PluginRegistryModel(Base):
    __tablename__ = 'plugin_registry_model'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    display_name = Column(String)
    icon = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    author = Column(String, nullable=True)
    url = Column(String, nullable=True)
    version = Column(String, nullable=True)
    settings_metadata = Column(JSON, nullable=True)
    is_enabled = Column(Boolean, default=False)

    # Relationship
    instances = relationship('PluginInstanceModel', back_populates='plugin')
    functions = relationship('FunctionRegistryModel', back_populates='plugin')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "icon": self.icon,
            "description": self.description,
            "author": self.author,
            "url": self.url,
            "version": self.version,
            "settings_metadata": self.settings_metadata,
            "functions": [function.serialize() for function in self.functions],
            "is_enabled": self.is_enabled
        }
