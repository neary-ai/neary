from typing import List, Optional
from pydantic import BaseModel

from modules.spaces.schemas import Space
from modules.llms.schemas import ChatModel
from modules.plugins.schemas import Plugin
from modules.presets.schemas import Preset
from modules.conversations.schemas import Conversation
from modules.messages.schemas import BookmarkDetails
from modules.integrations.schemas import Integration


class InitialData(BaseModel):
    app_state: Optional[dict] = None
    user_profile: dict
    spaces: List[Space]
    conversations: List[Conversation]
    models: List[ChatModel]
    plugins: List[Plugin]
    presets: List[Preset]
    integrations: List[Integration]
    bookmarks: List[BookmarkDetails]
