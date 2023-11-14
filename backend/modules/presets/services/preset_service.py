import os
import json
from typing import Optional

from sqlalchemy.orm import Session

from ..models import PresetModel
from ..schemas import PresetUpdate
from modules.conversations.models import ConversationModel
from modules.plugins.services.plugin_service import PluginService


class PresetService:
    def __init__(self, db: Session):
        self.db = db

    def create_preset(
        self,
        name: str,
        description: str,
        icon: str,
        plugins: dict,
        settings: dict,
        is_default: bool,
        is_custom: bool,
    ):
        preset = PresetModel(
            name=name,
            description=description,
            icon=icon,
            plugins=plugins,
            settings=settings,
            is_default=is_default,
            is_custom=is_custom,
        )
        self.db.add(preset)
        self.db.commit()
        self.db.refresh(preset)
        return preset

    def apply_preset(self, conversation: ConversationModel, preset_id: int = None):
        if preset_id is None:
            preset = self.get_default_preset()
        else:
            preset = self.get_preset_by_id(preset_id)

        conversation.preset = preset
        conversation.settings = preset.settings
        conversation.plugins = []

        for plugin in preset.plugins:
            PluginService(self.db).create_plugin_instance(
                plugin_name=plugin["name"],
                conversation=conversation,
                functions=plugin["functions"],
            )

        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def create_preset_from_conversation(
        self,
        conversation_id: int,
        name: str,
        description: str = None,
        icon: Optional[str] = None,
    ):
        conversation = (
            self.db.query(ConversationModel)
            .filter(ConversationModel.id == conversation_id)
            .first()
        )

        if conversation is None:
            raise ValueError(f"Conversation {conversation_id} not found")

        serialized_plugins = self._serialize_plugins_for_preset(conversation.plugins)

        preset = PresetModel(
            name=name,
            description=description,
            icon=icon,
            plugins=serialized_plugins,
            settings=conversation.settings,
            is_default=False,
            is_custom=True,
        )

        self.db.add(preset)
        self.db.commit()
        self.db.refresh(preset)
        return preset

    def _serialize_plugins_for_preset(self, plugins):
        serialized_plugins = []
        for plugin_instance in plugins:
            serialized_plugin = {
                "name": plugin_instance.plugin.name,
                "data": plugin_instance.data,
                "functions": [],
            }
            for function_instance in plugin_instance.function_instances:
                serialized_function = {
                    "name": function_instance.function.name,
                    "settings": function_instance.get_merged_settings(),
                    "type": function_instance.function.type,
                }
                serialized_plugin["functions"].append(serialized_function)
            serialized_plugins.append(serialized_plugin)
        return serialized_plugins

    def get_presets(self):
        return self.db.query(PresetModel).all()

    def get_preset_by_name(self, preset_name: str):
        return (
            self.db.query(PresetModel).filter(PresetModel.name == preset_name).first()
        )

    def get_preset_by_id(self, preset_id: int):
        return self.db.query(PresetModel).filter(PresetModel.id == preset_id).first()

    def get_default_preset(self):
        return self.db.query(PresetModel).filter(PresetModel.is_default == True).first()

    def update_preset(self, preset_id: int, preset_data: PresetUpdate):
        preset = self.get_preset_by_id(preset_id)
        if preset:
            update_data = (
                preset_data.model_dump(exclude_unset=True)
                if isinstance(preset_data, PresetUpdate)
                else preset_data
            )

            if "is_default" in update_data and update_data["is_default"]:
                # Set all presets is_default to False
                for p in self.get_presets():
                    if p.is_default:
                        p.is_default = False
                        self.db.commit()
                        self.db.refresh(p)

            for var, value in update_data.items():
                if value is not None:
                    setattr(preset, var, value)
            self.db.commit()
            self.db.refresh(preset)
            return preset
        else:
            return None

    def update_preset_from_conversation(self, preset_id: int, conversation_id: int):
        # Fetch the conversation and the preset
        conversation = (
            self.db.query(ConversationModel)
            .filter(ConversationModel.id == conversation_id)
            .first()
        )
        preset = self.get_preset_by_id(preset_id)

        if conversation is None:
            raise ValueError(f"Conversation {conversation_id} not found")

        if preset is None:
            raise ValueError(f"Preset {preset_id} not found")

        # Update the preset with the conversation data
        serialized_plugins = self._serialize_plugins_for_preset(conversation.plugins)
        preset.plugins = serialized_plugins
        preset.settings = conversation.settings

        self.db.commit()
        self.db.refresh(preset)
        return preset

    def delete_preset(self, preset_id: int):
        preset = self.get_preset_by_id(preset_id)

        if preset is None:
            raise ValueError(f"Preset {preset_id} not found")

        if preset.is_default:
            new_default = (
                self.db.query(PresetModel).filter(PresetModel.id != preset_id).first()
            )

            if new_default is not None:
                new_default.is_default = True

        self.db.delete(preset)

        default_preset = self.get_default_preset()

        conversations_with_deleted_preset = (
            self.db.query(ConversationModel)
            .filter(ConversationModel.preset_id == preset_id)
            .all()
        )

        for conversation in conversations_with_deleted_preset:
            self.apply_preset(conversation, default_preset.id)

        self.db.commit()

    def load_presets(self, file_path=None):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        file_path = file_path if file_path else os.path.join(parent_dir, "presets.json")

        with open(file_path, "r") as f:
            presets = json.load(f)

        for preset in presets:
            existing_preset = self.get_preset_by_name(preset["name"])

            if existing_preset is None:
                new_preset = PresetModel(**preset)
                self.db.add(new_preset)
            else:
                if not existing_preset.is_custom:
                    for key, value in preset.items():
                        setattr(existing_preset, key, value)

        self.db.commit()
