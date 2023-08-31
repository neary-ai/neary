from backend.plugins import BasePlugin, tool, snippet
from backend.services.user_profile_manager import UserProfileManager

class UserProfile(BasePlugin):
    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

    @snippet
    async def insert_user_profile(self, context):
        profile_manager = UserProfileManager()
        user_profile = await profile_manager.get_profile()
        
        if user_profile:
            profile_str = "Here is the user's profile. Remember to tailor your answers to their information where applicable:\n\n"
            for k, v in user_profile.items():
                profile_str += f"{k}: {v}\n"

            context.add_snippet(profile_str)

    @tool
    async def update_user_profile(self, fields):
        profile_manager = UserProfileManager()
        existing_profile = await profile_manager.get_profile()

        if existing_profile:
            await profile_manager.set_profile({**existing_profile, **fields})
        else:
            await profile_manager.set_profile(fields)

        return "The user's profile was updated!"