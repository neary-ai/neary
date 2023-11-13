from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Table, Text, Boolean
from sqlalchemy.orm import relationship

from database import Base

function_integration = Table(
    "function_integration",
    Base.metadata,
    Column("function_id", Integer, ForeignKey("function_model.id")),
    Column("integration_id", Integer, ForeignKey("integration_model.id")),
)


class FunctionInstanceModel(Base):
    __tablename__ = "function_instance_model"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    function_id = Column(Integer, ForeignKey("function_model.id"))
    plugin_instance_id = Column(Integer, ForeignKey("plugin_instance_model.id"))
    settings_values = Column(JSON, nullable=True)

    # Relationships
    function = relationship("FunctionModel", back_populates="instances")
    plugin_instance = relationship(
        "PluginInstanceModel", back_populates="function_instances"
    )

    def get_merged_settings(self):
        settings_metadata = self.function.settings_metadata
        settings_values = self.settings_values

        if settings_metadata:
            for key, meta in settings_metadata.items():
                if settings_values and key in settings_values:
                    meta["value"] = settings_values[key]["value"]
            return settings_metadata

        return None


class FunctionModel(Base):
    __tablename__ = "function_model"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    display_name = Column(String)
    description = Column(Text, nullable=True)
    llm_description = Column(Text, nullable=True)
    plugin_id = Column(Integer, ForeignKey("plugin_model.id"))
    settings_metadata = Column(JSON, nullable=True)
    parameters = Column(JSON, nullable=True)
    meta_data = Column(JSON, nullable=True)

    plugin = relationship("PluginModel", back_populates="functions")
    integrations = relationship(
        "IntegrationModel",
        secondary=function_integration,
        back_populates="functions",
    )

    instances = relationship("FunctionInstanceModel", back_populates="function")


class PluginInstanceModel(Base):
    __tablename__ = "plugin_instance_model"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    plugin_id = Column(Integer, ForeignKey("plugin_model.id"))
    conversation_id = Column(Integer, ForeignKey("conversation_model.id"))
    settings_values = Column(JSON, nullable=True)
    data = Column(JSON, nullable=True)

    plugin = relationship("PluginModel", back_populates="instances")
    conversation = relationship("ConversationModel", back_populates="plugins")
    function_instances = relationship(
        "FunctionInstanceModel", back_populates="plugin_instance"
    )

    def get_merged_settings(self):
        settings_metadata = self.plugin.settings_metadata
        settings_values = self.settings_values

        if settings_metadata:
            for key, meta in settings_metadata.items():
                if settings_values and key in settings_values:
                    meta["value"] = settings_values[key]
            return settings_metadata

        return None


class PluginModel(Base):
    __tablename__ = "plugin_model"

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

    instances = relationship("PluginInstanceModel", back_populates="plugin")
    functions = relationship("FunctionModel", back_populates="plugin")
