from sqlalchemy import Column, Integer, String, Text, Boolean, JSON
from sqlalchemy.orm import relationship

from database import Base


class PresetModel(Base):
    __tablename__ = "preset_model"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    plugins = Column(JSON, nullable=True)
    settings = Column(JSON, nullable=True)
    is_default = Column(Boolean, default=False)
    is_custom = Column(Boolean, default=False)

    conversations = relationship("ConversationModel", back_populates="preset")
