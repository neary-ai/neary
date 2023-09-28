from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import Base

class FunctionInstanceModel(Base):
    __tablename__ = 'function_instance_model'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    function_id = Column(Integer, ForeignKey('function_registry_model.id'))
    plugin_instance_id = Column(Integer, ForeignKey('plugin_instance_model.id'))
    settings_values = Column(JSON, nullable=True)

    # Relationships
    function = relationship('FunctionRegistryModel', back_populates='instances')
    plugin_instance = relationship('PluginInstanceModel', back_populates='function_instances')

    def merge_settings(self, metadata, values):
        if metadata:
            for key, meta in metadata.items():
                if values and key in values:
                    meta['value'] = values[key]
            return metadata

    def serialize(self):
        # SQLAlchemy operates synchronously, so we don't need the `async` keyword.
        # We assume here that related entities are already loaded into the session.
        serialized_function = self.function.serialize()

        return {
            'name' : self.name,
            'type': self.function.type,
            'settings': self.merge_settings(self.function.settings_metadata, self.settings_values),
            'integrations': serialized_function['integrations'],
            'metadata': self.function.meta_data
        }
