from backend.database import SessionLocal
from backend.services import user_service

class UserProfileManager:
    def __init__(self):
        self.db = SessionLocal()
    
    async def get_profile(self):
        return user_service.get_profile(self.db)

    async def set_profile(self, profile_data):
        return user_service.set_profile(self.db, profile_data)

    async def get_profile_field(self, key):
        return user_service.get_profile_field(self.db, key)

    async def set_profile_field(self, key, value):
        return user_service.set_profile_field(self.db, key, value)

    async def delete_profile_field(self, key):
        return user_service.delete_profile_field(self.db, key)