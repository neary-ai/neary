import jwt
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session

from config import settings
from .models import UserModel

ENABLE_AUTH = settings.application.get("ENABLE_AUTH", False)
JWT_SECRET = settings.application.get("JWT_SECRET", "your-secret-key")
ALGORITHM = "HS256"


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_current_user(self, request: Request):
        token = request.cookies.get("access_token")
        if token:
            try:
                jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
            except jwt.PyJWTError:
                if ENABLE_AUTH:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                    )
        elif ENABLE_AUTH:
            user = self.get_user_by_id(1)
            if user is None or user.email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="initial_start"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
                )

        user = self.get_user_by_id(1)

        if user is None and not ENABLE_AUTH:
            user_data = {}
            user = self.create_user(user_data)

        return user

    def get_user(self):
        user = self.db.query(UserModel).first()
        if user is None:
            user = self.create_user({})
        return user

    def get_user_by_id(self, user_id: int):
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()

    def get_user_by_email(self, email: str):
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def create_user(self, user_data):
        user = UserModel(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user: UserModel, user_data):
        for key, value in user_data.items():
            setattr(user, key, value)
        self.db.commit()
        return user

    def get_profile(self):
        user = self.get_user_by_id(1)
        return user.profile if user else None

    def set_profile(self, profile_data: dict):
        user = self.get_user_by_id(1)
        if user:
            user.profile = profile_data
            self.db.commit()
        return user.profile if user else None

    def get_profile_field(self, key: str):
        user = self.get_user_by_id(1)
        return user.profile.get(key) if user else None

    def set_profile_field(self, key: str, value: str):
        user = self.get_user_by_id(1)
        if user:
            user.profile[key] = value
            self.db.commit()
        return user.profile if user else None

    def delete_profile_field(self, key: str):
        user = self.get_user_by_id(1)
        if user and key in user.profile:
            del user.profile[key]
            self.db.commit()
        return user.profile if user else None

    def get_state(self):
        user = self.get_user()
        state_data = user.app_state
        state_data["profile"] = user.profile
        return state_data

    def update_app_state(self, state_data: dict):
        user = self.get_user()
        user.app_state = state_data
        self.db.commit()
