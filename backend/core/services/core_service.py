import os
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from config import settings
from core.schemas import InitialData
from users.services import UserService
from modules.spaces.services.space_service import SpaceService
from modules.plugins.services.plugin_service import PluginService
from modules.presets.services.preset_service import PresetService
from modules.integrations.services.integration_service import IntegrationService
from modules.conversations.services.conversation_service import ConversationService

from modules.conversations.schemas import *
from modules.conversations.models import *


class InitService:
    def __init__(self, db: Session):
        self.db = db

    def initialize_app(self):
        user_service = UserService(self.db)
        conversation_service = ConversationService(self.db)

        user = user_service.get_user()
        conversations = conversation_service.get_conversations()

        # Create welcome conversation if first start
        if not user.app_state and not conversations:
            conversations = [
                conversation_service.create_conversation(title="New conversation")
            ]

        initial_data = InitialData(
            app_state=user.app_state,
            user_profile=user.profile,
            spaces=SpaceService(self.db).get_spaces(),
            conversations=conversations,
            plugins=PluginService(self.db).get_plugins(),
            presets=PresetService(self.db).get_presets(),
            integrations=IntegrationService(self.db).get_integrations(),
        )

        return initial_data


class FileService:
    def __init__(self, conversation_id):
        base_directory = (
            Path(__file__).resolve().parent.parent.parent / "data" / "files"
        )
        self.conversation_id = conversation_id
        self.file_directory = os.path.join(base_directory, str(self.conversation_id))

    def save_file(self, file_obj, filename=None, extension="txt"):
        """Save a file to the conversation's subdirectory."""
        # Generate a random filename if none is provided
        if filename is None:
            filename = f"{uuid.uuid4()}"
        filename = f"{filename}.{extension}"

        # Ensure the directory exists
        os.makedirs(self.file_directory, exist_ok=True)

        # Full path to the file
        filepath = os.path.join(self.file_directory, filename)

        # Write the file
        with open(filepath, "wb") as out_file:
            out_file.write(file_obj.read())

        # Get file size in bytes
        file_size = os.path.getsize(filepath)

        # Return the filepath, filename, and url
        return {
            "filepath": filepath,
            "filename": filename,
            "filesize": self._format_size(file_size),
            "url": self.get_file_url_path(filename),
        }

    def get_file(self, filename):
        """Return the full path to a file in the plugin's subdirectory."""
        return os.path.join(self.file_directory, filename)

    def get_file_url_path(self, filename):
        """Return a URL for a file in the plugin's subdirectory."""
        return f"{settings.APPLICATION.base_url}/api/files/{self.conversation_id}/{filename}"

    def delete_file(self, filename):
        """Delete a file in the plugin's subdirectory."""
        filepath = self.get_file(filename)
        os.remove(filepath)

    def _format_size(self, size):
        """Take a size in bytes and return it in a human-readable format."""
        # Convert size in bytes to kilobytes
        size /= 1024.0

        # Define the thresholds for each size unit
        units = {"KB": 0, "MB": 1, "GB": 2, "TB": 3}
        unit = "KB"

        # Keep dividing the size by 1024 until it's under 1024
        for unit, threshold in units.items():
            if size < 1024.0 or unit == "TB":  # we don't go beyond TB
                break
            size /= 1024.0

        # Format the size with the appropriate unit
        return f"{size:.2f} {unit}"
