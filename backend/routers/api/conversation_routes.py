from typing import Optional

from fastapi import HTTPException, status, Request, APIRouter, Body
from fastapi.responses import JSONResponse,  FileResponse

from backend.models import *
from backend.utils.utils import export_conversation

router = APIRouter()

@router.get("")
async def get_conversations(space_id: int = Body(...)):
    """Get conversations"""
    if space_id == -1:
        conversations = await ConversationModel.filter(is_archived=False).order_by("-updated_at")
    else:
        conversations = await ConversationModel.filter(is_archived=False, space_id=space_id).order_by("-updated_at")
    
    serialized_conversations = [await conversation.serialize() for conversation in conversations]

    return serialized_conversations

@router.post("")
async def create_conversation(request: Request):
    """Create a conversation"""
    data = await request.json()
    space_id = data['space_id']

    space = await SpaceModel.get_or_none(id=space_id)

    preset = await PresetModel.filter(is_default=True).first()

    conversation = await ConversationModel.create(title="New Conversation", space=space, preset=preset, settings=preset.settings)

    for plugin in preset.plugins:
        plugin_registry = await PluginRegistryModel.get_or_none(name=plugin["name"])
        if plugin_registry:
            plugin_registry.is_enabled = True
            await plugin_registry.save()

            # Create plugin instance
            plugin_instance = await PluginInstanceModel.create(name=plugin["name"], plugin=plugin_registry, settings_values=plugin.get("settings", None), conversation=conversation)
            
            # Create function instances
            for function in plugin["functions"]:
                function_name = function["name"]
                function_details = await FunctionRegistryModel.get_or_none(name=function_name)
                if function_details:
                    await FunctionInstanceModel.create(name=function_name, function=function_details, plugin_instance=plugin_instance, settings_values=function.get('settings', None))
    
    return await conversation.serialize()

@router.get("/settings")
async def get_settings_options():
    # TO-DO: Move these to config file
    options = {
        "llm": {
            "api_type": [
                {
                    "option": "OpenAI",
                    "value": "openai",
                },
                {
                    "option": "Azure",
                    "value": "azure",
                },
                {
                    "option": "Custom",
                    "value": "custom",
                },
            ],
            "model": [
                {
                    "option": "gpt-4",
                    "value": "gpt-4"
                },
                {
                    "option": "gpt-3.5-turbo",
                    "value": "gpt-3.5-turbo"
                },
            ]
        }
    }

    return options

@router.get("/{conversation_id}")
async def get_conversation(conversation_id: int = None):
    """Get a single conversation"""
    conversation = await ConversationModel.get_or_none(id=conversation_id, is_archived=False)
    if conversation:
        return await conversation.serialize()
    else:
        print('Conversation not found!')


@router.patch("/{conversation_id}")
async def archive_conversation(conversation_id: int):
    """Archive a conversation"""

    conversation = await ConversationModel.get_or_none(id=conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Conversation not found")

    conversation.is_archived = True
    await conversation.save()
    return {"detail": "Conversation archived"}


@router.put("/{conversation_id}")
async def update_conversation(request: Request, conversation_id: int):
    """Update a conversation's settings"""
    conversation_data = await request.json()

    conversation = await ConversationModel.get_or_none(id=conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Fetch related plugins
    await conversation.fetch_related('plugins')

    # Update fields
    conversation.title = conversation_data.get('title', conversation.title)
    conversation.settings = conversation_data.get(
        'settings', conversation.settings)

    # Update space
    space_id = conversation_data.get('space_id')
    if space_id:
        space = await SpaceModel.get_or_none(id=space_id)
        conversation.space = space

    # Update preset
    new_preset = False
    new_plugin_data = None

    preset_data = conversation_data.get('preset')
    if preset_data:
        preset_id = preset_data.get('id')

        if preset_id != conversation.preset_id:
            new_preset = True
            preset = await PresetModel.get_or_none(id=preset_id)
            if not preset:
                raise HTTPException(status_code=404, detail="Preset not found")

            conversation.preset = preset
            conversation.settings = preset.settings
            
            # Update conversation settings with preset settings
            new_plugin_data = preset.plugins

    # If no new plugins from preset, get from settings
    if new_plugin_data is None:
        new_plugin_data = conversation_data.get('plugins', None)

    # Existing plugin names
    existing_plugin_names = [plugin.name for plugin in conversation.plugins]

    # New plugin names
    new_plugin_names = [plugin["name"] for plugin in new_plugin_data]

    # Plugin names to remove
    plugins_to_remove = set(existing_plugin_names) - set(new_plugin_names)

    # Remove plugins that are not included in the new data
    for plugin_name in plugins_to_remove:
        plugin_registry = await PluginRegistryModel.get_or_none(name=plugin_name)
        plugin_instance = await PluginInstanceModel.get_or_none(plugin=plugin_registry, conversation=conversation)
        if plugin_instance:
            await plugin_instance.delete()

    # Now add, remove or update plugins from conversation model
    for plugin in new_plugin_data:
        
        # See if instance already exists
        plugin_registry = await PluginRegistryModel.get_or_none(name=plugin["name"])

        if plugin_registry is None:
            print('Plugin not found: ', plugin["name"])
            continue

        plugin_instance = await PluginInstanceModel.get_or_none(plugin=plugin_registry, conversation=conversation)

        # Create or update plugin instance
        if plugin_instance is None:
            plugin_instance = await PluginInstanceModel.create(name=plugin["name"], plugin=plugin_registry, conversation=conversation, settings_values=plugin.get('settings', None))
    
        # Create or update function instances
        function_instances = await plugin_instance.function_instances

        for function in plugin["functions"]:
            function_name = function["name"]
            settings = function.get('settings') or {}
            settings_values = {key: value['value'] if isinstance(value, dict) and 'value' in value else value for key, value in settings.items()}
            
            existing_function_instance = None
            for instance in function_instances:
                if instance.name == function_name:
                    existing_function_instance = instance

            if existing_function_instance:
                existing_function_instance.settings_values = settings_values
                await existing_function_instance.save()
            else:
                function_registry = await FunctionRegistryModel.get_or_none(name=function_name)
                if function_registry:
                    await FunctionInstanceModel.create(name=function_name, function=function_registry, plugin_instance=plugin_instance, settings_values=settings_values)
                else:
                    print ('Function not found: ', function_name)

        # Remove function instances that are not in the frontend data anymore
        for instance in function_instances:
            if not any(function["name"] == instance.name for function in plugin["functions"]):
                await instance.delete()

        # Enable plugins if new preset
        if new_preset:
            plugin_registry.is_enabled = True
            await plugin_registry.save()

    await conversation.save()

    output = await conversation.serialize()

    return output


@router.get("/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: int, archived: Optional[bool] = False):
    """Get a conversation's messages"""
    conversation = await ConversationModel.get_or_none(id=conversation_id)
    if conversation:
        if archived:
            messages = await conversation.messages.all()
        else:
            messages = await conversation.messages.filter(is_archived=False).all()

        serialized_messages = [message.serialize() for message in messages]
        return {"messages": serialized_messages}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.post("/{conversation_id}/messages/archive")
async def archive_conversation_messages(conversation_id: int):
    """Archive a conversation's messages"""
    conversation = await ConversationModel.get_or_none(id=conversation_id)
    if conversation:
        messages = await conversation.messages.all()
        for message in messages:
            message.is_archived = True
            await message.save()
        return JSONResponse(content={"status": "success"})
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.get("/{conversation_id}/export")
async def export_conversation_data(conversation_id: int, export_format: str = 'txt'):
    """Export a conversation's messages in plain text or JSON format"""
    exported_data = await export_conversation(conversation_id, export_format)

    file_name = f"conversation_{conversation_id}"
    file_name += ".txt" if export_format == "txt" else ".json"

    with open(file_name, "w") as f:
        f.write(exported_data)

    return FileResponse(file_name, media_type="application/octet-stream", filename=file_name)