from backend.models import UserModel

class UserProfileManager:
    def __init__(self):
        pass

    async def get_profile(self):
        """
        Fetches the profile of the first user in the database.

        Returns:
            dict: The profile of the first user.
        """
        user = await UserModel.first()
        return user.profile

    async def set_profile(self, profile_data):
        """
        Sets the profile of the first user in the database with the provided data.

        Args:
            profile_data (dict): The new profile data.

        Returns:
            dict: The updated profile of the first user.
        """
        user = await UserModel.first()
        user.profile = profile_data
        await user.save()
        return user.profile

    async def get_field(self, key):
        """
        Fetches the value of a specific field in the profile of the first user.

        Args:
            key (str): The key of the field to fetch.

        Returns:
            The value of the field, or None if the field is not present.
        """
        user = await UserModel.first()
        return user.profile.get(key)

    async def set_field(self, key, value):
        """
        Sets the value of a specific field in the profile of the first user.

        Args:
            key (str): The key of the field to set.
            value: The new value for the field.

        Returns:
            dict: The updated profile of the first user.
        """
        user = await UserModel.first()
        user.profile[key] = value
        await user.save()
        return user.profile

    async def delete_field(self, key):
        """
        Deletes a specific field from the profile of the first user.

        Args:
            key (str): The key of the field to delete.

        Returns:
            dict: The updated profile of the first user.
        """
        user = await UserModel.first()
        if key in user.profile:
            del user.profile[key]
            await user.save()
        return user.profile