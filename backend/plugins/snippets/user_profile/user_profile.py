from backend.plugins import Snippet
from backend.services.user_profile_manager import UserProfileManager

class UserProfileSnippet(Snippet):
    name = "user_profile"
    display_name = "User Profile"
    description = "Returns the contents of the user profile"

    def __init__(self, id, conversation, settings=None, data=None):
        super().__init__(id, conversation, settings, data)

    async def run(self, context):
        profile_manager = UserProfileManager()
        user_profile = await profile_manager.get_profile()
        
        if user_profile:
            profile_str = "Here is the user's profile. Remember to tailor your answers to their information where applicable:\n\n"
            for k, v in user_profile.items():
                profile_str += f"{k}: {v}\n"

            context.add_snippet(profile_str)