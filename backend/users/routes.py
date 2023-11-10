import json
from pathlib import Path

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from .services import UserService

router = APIRouter()


@router.put("/profile")
async def update_user_profile(profile_data: dict):
    UserService.set_profile(profile_data)
    return {"detail": "Profile updated successfully"}
