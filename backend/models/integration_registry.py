from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship

from .base import Base
from .function_registry import function_integration

class IntegrationRegistryModel(Base):
    __tablename__ = 'integration_registry_model'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    display_name = Column(String)
    auth_method = Column(String)
    data = Column(JSON)

    # Relationships
    instances = relationship('IntegrationInstanceModel', back_populates='integration')
    functions = relationship('FunctionRegistryModel', secondary=function_integration, back_populates='integrations')

    @property
    def is_integrated(self):
        return len(self.instances) > 0

    def serialize(self):
        # SQLAlchemy operates synchronously, so we don't need the `async` keyword.
        # We assume here that related entities are already loaded into the session.

        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "auth_method": self.auth_method,
            "data": self.data,
            "is_integrated": self.is_integrated
        }
