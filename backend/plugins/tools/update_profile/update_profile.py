from backend.models import UserModel
from backend.plugins import Tool
from backend.services import UserProfileManager

class UpdateProfileTool(Tool):
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

    async def run(self, fields):
        profile_manager = UserProfileManager()
        existing_profile = await profile_manager.get_profile()

        if existing_profile:
            await profile_manager.set_profile({**existing_profile, **fields})
        else:
            await profile_manager.set_profile(fields)

        return "The user's profile was updated!"