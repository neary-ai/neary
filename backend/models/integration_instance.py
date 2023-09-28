from sqlalchemy import Column, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import Base

class IntegrationInstanceModel(Base):
    __tablename__ = 'integration_instance_model'

    id = Column(Integer, primary_key=True)
    integration_id = Column(Integer, ForeignKey('integration_registry_model.id'))
    credentials = Column(JSON)

    # Relationship
    integration = relationship('IntegrationRegistryModel', back_populates='instances')
