from datetime import datetime

from sqlalchemy.orm import Session
from backend import models
from backend.services import plugin_service


def get_conversation_by_id(db: Session, conversation_id: int):
    return db.query(models.ConversationModel).filter(models.ConversationModel.id == conversation_id).first()

def get_conversations_by_space(db: Session, space_id: int):
    return db.query(models.ConversationModel).filter(models.ConversationModel.space_id == space_id).all()

def get_conversations(db: Session, space_id: int):
    if space_id == -1:
        return db.query(models.ConversationModel).filter(models.ConversationModel.is_archived == False).order_by(models.ConversationModel.updated_at.desc()).all()
    else:
        return db.query(models.ConversationModel).filter(models.ConversationModel.is_archived == False, models.ConversationModel.space_id == space_id).order_by(models.ConversationModel.updated_at.desc()).all()

def get_active_conversations(db: Session):
    return db.query(models.ConversationModel).filter(models.ConversationModel.is_archived == False).order_by(models.ConversationModel.updated_at.desc()).all()

def update_conversation(db: Session, conversation: models.ConversationModel, conversation_data: dict):
    conversation.title = conversation_data.get('title', conversation.title)
    conversation.settings = conversation_data.get(
        'settings', conversation.settings)
    db.commit()


def update_conversation_timestamp(db: Session, conversation: models.ConversationModel):
    conversation.updated_at = datetime.utcnow()
    db.commit()


def archive_conversation(db: Session, conversation: models.ConversationModel):
    conversation.is_archived = True
    db.commit()


def update_conversation_settings(db: Session, conversation: models.ConversationModel, settings: dict):
    conversation.settings = settings
    db.commit()


def create_conversation(db: Session, space_id: int = None, title: str = "New Conversation", preset: models.PresetModel = None):
    space = db.query(models.SpaceModel).filter_by(id=space_id).first() if space_id else None
    preset = preset if preset else db.query(models.PresetModel).filter_by(is_default=True).first()
    conversation = models.ConversationModel(
        title=title, space=space, preset=preset, settings=preset.settings)

    db.add(conversation)
    db.flush()  # flush the changes to assign an ID to conversation

    for plugin in preset.plugins:
        plugin_service.create_plugin_instance(db, plugin, conversation)

    db.commit()
    db.refresh(conversation)

    return conversation


def create_conversation_and_plugins(db: Session, space_id: int, plugins: list):
    conversation = create_conversation(db, space_id)
    for plugin in plugins:
        plugin_service.create_plugin_instance(db, plugin, conversation)
    return conversation


def update_conversation_space(db: Session, conversation: models.ConversationModel, space_id: int = None):
    space = db.query(models.SpaceModel).filter_by(id=space_id).first() if space_id else None
    conversation.space = space
    db.commit()


def update_conversation_preset(db: Session, conversation: models.ConversationModel, preset_data: dict):
    if preset_data:
        preset_id = preset_data.get('id')
        if preset_id != conversation.preset_id:
            preset = db.query(models.PresetModel).filter_by(
                id=preset_id).first()
            conversation.preset = preset
            conversation.settings = preset.settings
            db.commit()


def remove_plugins(db: Session, conversation: models.ConversationModel, plugins_to_remove: set):
    for plugin_name in plugins_to_remove:
        plugin_registry = db.query(models.PluginRegistryModel).filter_by(
            name=plugin_name).first()
        plugin_instance = db.query(models.PluginInstanceModel).filter_by(
            plugin=plugin_registry, conversation=conversation).first()
        if plugin_instance:
            db.delete(plugin_instance)
            db.commit()


def update_plugin_instance(db: Session, conversation: models.ConversationModel, plugin: dict):
    plugin_registry = db.query(models.PluginRegistryModel).filter_by(
        name=plugin["name"]).first()
    if plugin_registry is None:
        print('Plugin not found: ', plugin["name"])
        return
    plugin_instance = db.query(models.PluginInstanceModel).filter_by(
        plugin=plugin_registry, conversation=conversation).first()
    if plugin_instance is None:
        plugin_instance = models.PluginInstanceModel(
            name=plugin["name"], plugin=plugin_registry, conversation=conversation, settings_values=plugin.get('settings', None))
        db.add(plugin_instance)
        db.commit()
    return plugin_instance


def enable_plugin(db: Session, plugin_registry: models.PluginRegistryModel):
    plugin_registry.is_enabled = True
    db.commit()


def update_conversation_plugins(db: Session, conversation: models.ConversationModel, new_plugin_data: list):
    existing_plugin_names = [plugin.name for plugin in conversation.plugins]
    new_plugin_names = [plugin["name"] for plugin in new_plugin_data]
    plugins_to_remove = set(existing_plugin_names) - set(new_plugin_names)

    remove_plugins(db, conversation, plugins_to_remove)

    for plugin in new_plugin_data:
        plugin_instance = update_plugin_instance(db, conversation, plugin)
        if plugin_instance:
            plugin_service.enable_plugin(db, plugin_instance.plugin)
            plugin_service.update_function_instances(
                db, plugin_instance, plugin["functions"])
            plugin_service.remove_function_instances(
                db, plugin_instance, plugin["functions"])

def add_document_to_conversation(db: Session, conversation: models.ConversationModel, document: models.DocumentModel):
    conversation.documents.append(document)
    db.commit()

def remove_document_from_conversation(db: Session, conversation: models.ConversationModel, document: models.DocumentModel):
    conversation.documents.remove(document)
    db.commit()