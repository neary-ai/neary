from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from database import get_db
from .services import UserService

router = APIRouter()


@router.put("/profile")
async def update_user_profile(profile_data: dict, db: Session = Depends(get_db)):
    UserService(db).set_profile(profile_data)
    return {"detail": "Profile updated successfully"}
