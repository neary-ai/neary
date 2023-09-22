from backend.models import UserModel

class UserProfileManager:

    async def get_profile(self):
        user = await UserModel.first()
        return user.profile

    async def set_profile(self, profile_data):
        user = await UserModel.first()
        user.profile = profile_data
        await user.save()
        return user.profile

    async def get_profile_field(self, key):
        user = await UserModel.first()
        return user.profile.get(key)

    async def set_profile_field(self, key, value):
        user = await UserModel.first()
        user.profile[key] = value
        await user.save()
        return user.profile

    async def delete_profile_field(self, key):
        user = await UserModel.first()
        if key in user.profile:
            del user.profile[key]
            await user.save()
        return user.profile