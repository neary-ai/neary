from backend.models import UserModel
from backend.plugins import Tool
from backend.services import UserProfileManager


class UpdateProfileTool(Tool):
    name = "update_profile"
    display_name = "Update Profile"
    description = "Adds information to your profile"
    llm_description = "`update_profile`: Updates the user's profile with new information. Takes a `fields` (json) argument that contains key-value pairs of the information to be added or updated. E.g. {'name': 'Joe', 'timezone': 'America/Denver'}."

    requires_approval = True
    follow_up_on_output = True

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
