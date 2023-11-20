import json
from typing import List

from sqlalchemy.orm import Session

from modules.messages.schemas import MessageBase
from modules.presets.services.preset_service import PresetService
from modules.plugins.services.plugin_service import PluginService
from modules.spaces.services.space_service import SpaceService
from modules.messages.services.message_service import MessageService
from ..models import ConversationModel


class ConversationService:
    def __init__(self, db: Session):
        self.db = db

    def create_conversation(
        self,
        title: str = "New conversation",
        preset_id: int = None,
        space_id: int = None,
    ):
        space = SpaceService(self.db).get_space_by_id(space_id) if space_id else None

        conversation = ConversationModel(title=title, space=space)
        self.db.add(conversation)
        self.db.commit()

        PresetService(self.db).apply_preset(conversation, preset_id)

        self.db.refresh(conversation)

        return conversation

    def update_conversation(
        self, conversation: ConversationModel, conversation_data: dict
    ):
        """Update title, space and settings."""
        conversation.title = conversation_data.get("title", conversation.title)
        conversation.settings = conversation_data.get("settings", conversation.settings)

        space_id = conversation_data.get("space_id")
        space = SpaceService(self.db).get_space_by_id(space_id) if space_id else None

        conversation.space = space

        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def add_conversation_function(
        self, function_name: str, plugin_name: str, conversation: ConversationModel
    ):
        """Add a function (tool/snippet) to a conversation"""
        existing_plugins = PluginService(self.db).get_plugins_by_conversation(
            conversation
        )
        plugin_instance = next(
            (plugin for plugin in existing_plugins if plugin.name == plugin_name), None
        )

        # Create the parent plugin
        if not plugin_instance:
            plugin_instance = PluginService(self.db).create_plugin_instance(
                plugin_name, conversation
            )

        # Then create the function instance
        existing_functions = PluginService(self.db).get_functions_by_conversation(
            conversation
        )
        function_instance = next(
            (
                function
                for function in existing_functions
                if function.name == function_name
            ),
            None,
        )

        if not function_instance:
            PluginService(self.db).create_function_instance(
                function_name, plugin_instance
            )

        self.db.refresh(conversation)

        return conversation

    def remove_conversation_function(
        self, function_name: str, conversation: ConversationModel
    ):
        PluginService(self.db).delete_function_instance(function_name, conversation)
        self.db.refresh(conversation)
        return conversation

    def get_conversation_by_id(self, conversation_id: int):
        return (
            self.db.query(ConversationModel)
            .filter(ConversationModel.id == conversation_id)
            .first()
        )

    def get_conversations(self, space_id: int = None):
        if space_id:
            return (
                self.db.query(ConversationModel)
                .filter(
                    ConversationModel.is_archived == False,
                    ConversationModel.space_id == space_id,
                )
                .order_by(ConversationModel.updated_at.desc())
                .all()
            )
        else:
            return (
                self.db.query(ConversationModel)
                .filter(ConversationModel.is_archived == False)
                .order_by(ConversationModel.updated_at.desc())
                .all()
            )

    def get_conversation_messages(
        self, conversation: ConversationModel, archived=False
    ) -> List[MessageBase]:
        db_messages = MessageService(self.db).get_messages_by_conversation_id(
            conversation.id, archived=archived
        )

        messages = [
            MessageBase.model_validate(db_message) for db_message in db_messages
        ]

        return messages

    def delete_conversation(self, conversation_id: int):
        conversation = (
            self.db.query(ConversationModel)
            .filter(ConversationModel.id == conversation_id)
            .first()
        )

        if not conversation:
            return False

        self.db.delete(conversation)
        self.db.commit()

        return True

    def export_conversation(self, conversation_id: int, export_format: str = "plain"):
        messages = MessageService(self.db).get_messages_by_conversation_id(
            conversation_id
        )

        file_name = f"conversation_{conversation_id}"
        file_name += ".txt" if export_format == "plain" else ".json"

        with open(file_name, "w") as f:
            if export_format == "plain":
                result = ""
                for message in messages:
                    sender = "Assistant" if message.role == "assistant" else "User"
                    result += f"[{message.created_at.isoformat()}] {sender}: {message.content}\n"
                f.write(result.rstrip())

            elif export_format == "json":
                result = []
                for message in messages:
                    sender = "Assistant" if message.role == "assistant" else "User"
                    result.append(
                        {
                            "created_at": message.created_at.isoformat(),
                            "sender": sender,
                            "content": message.content,
                        }
                    )
                f.write(json.dumps(result))

            else:
                raise ValueError(
                    "Invalid export format. Choose either 'plain' or 'json'."
                )

        return file_name
