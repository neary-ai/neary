import json

from sqlalchemy.orm import Session

from database import SessionLocal
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
