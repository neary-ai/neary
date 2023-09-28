from sqlalchemy.orm import Session
from backend import models

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.UserModel).filter(models.UserModel.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.UserModel).filter(models.UserModel.email == email).first()

def create_user(db: Session, user_data):
    user = models.UserModel(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user: models.UserModel, user_data):
    for key, value in user_data.items():
        setattr(user, key, value)
    db.commit()
    return user

def get_profile(db: Session):
    user = get_user_by_id(db, 1)
    return user.profile if user else None

def set_profile(db: Session, profile_data: dict):
    user = get_user_by_id(db, 1)
    if user:
        user.profile = profile_data
        db.commit()
    return user.profile if user else None

def get_profile_field(db: Session, key: str):
    user = get_user_by_id(db, 1)
    return user.profile.get(key) if user else None

def set_profile_field(db: Session, key: str, value: str):
    user = get_user_by_id(db, 1)
    if user:
        user.profile[key] = value
        db.commit()
    return user.profile if user else None

def delete_profile_field(db: Session, key: str):
    user = get_user_by_id(db, 1)
    if user and key in user.profile:
        del user.profile[key]
        db.commit()
    return user.profile if user else None