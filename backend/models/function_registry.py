from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship

from .base import Base

# Define the integration association table
function_integration = Table(
    'function_integration',
    Base.metadata,
    Column('function_id', Integer, ForeignKey('function_registry_model.id')),
    Column('integration_id', Integer, ForeignKey('integration_registry_model.id'))
)

class FunctionRegistryModel(Base):
    __tablename__ = 'function_registry_model'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    plugin_id = Column(Integer, ForeignKey('plugin_registry_model.id'))
    settings_metadata = Column(JSON, nullable=True)
    parameters = Column(JSON, nullable=True)
    meta_data = Column(JSON, nullable=True)

    # Relationships
    plugin = relationship('PluginRegistryModel', back_populates='functions')
    integrations = relationship('IntegrationRegistryModel', secondary=function_integration, back_populates='functions')
    instances = relationship('FunctionInstanceModel', back_populates='function')

    def serialize(self):
        # SQLAlchemy operates synchronously, so we don't need the `async` keyword.
        # We assume here that related entities are already loaded into the session.
        serialized_integrations = [integration.serialize() for integration in self.integrations]

        return {
            'name': self.name,
            'type': self.type,
            'settings_metadata': self.settings_metadata,
            'parameters': self.parameters,
            'integrations': [{'name': integration['display_name'], 'connected': integration['is_integrated']} for integration in serialized_integrations],
            'metadata': self.meta_data
        }
