from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import Base

class PluginInstanceModel(Base):
    __tablename__ = 'plugin_instance_model'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    plugin_id = Column(Integer, ForeignKey('plugin_registry_model.id'))
    conversation_id = Column(Integer, ForeignKey('conversation_model.id'))
    settings_values = Column(JSON, nullable=True)
    data = Column(JSON, nullable=True)

    # Relationships
    plugin = relationship('PluginRegistryModel', back_populates='instances')
    conversation = relationship('ConversationModel', back_populates='plugins')
    function_instances = relationship('FunctionInstanceModel', back_populates='plugin_instance')

    def merge_settings(self, metadata, values):
        if metadata:
            for key, meta in metadata.items():
                if values and key in values:
                    meta['value'] = values[key]
            return metadata

    def serialize(self):
        # SQLAlchemy operates synchronously, so we don't need the `async` keyword.
        # We assume here that related entities are already loaded into the session.
        function_instances = self.function_instances

        return {
            "id": self.id,
            "plugin_id": self.plugin.id,
            "conversation_id": self.conversation_id,
            "name": self.name,
            "display_name": self.plugin.display_name,
            "icon": self.plugin.icon,
            "description": self.plugin.description,
            "author": self.plugin.author,
            "url": self.plugin.url,
            "version": self.plugin.version,
            "settings": self.merge_settings(self.plugin.settings_metadata, self.settings_values),
            "data": self.data,
            "functions": [function.serialize() for function in function_instances],
            "is_enabled": self.plugin.is_enabled
        }
