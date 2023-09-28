from sqlalchemy import Column, Integer, String, JSON

from .base import Base

class UserModel(Base):
    """
    Represents the user in the system, storing authentication data and application-specific state.
    """
    __tablename__ = 'user_model'

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    profile = Column(JSON, default={"name": "", "location": "", "notes": ""})
    app_state = Column(JSON, nullable=True)