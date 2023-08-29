import os
import json
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, status, Request, APIRouter, Body, UploadFile, File
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse

from backend.models import *
from backend.auth import get_current_user
from backend.utils.utils import export_conversation
from backend.services.documents.document_manager import DocumentManager
from backend.conversation import Conversation

from backend.models import UserModel, IntegrationRegistryModel
from backend.services.oauth_handler import OAuthHandler

router = APIRouter()

"""
User Profile
"""


@router.put("/profile")
async def update_user_profile(request: Request):
    # Fetch the user from the database (this is just a placeholder)
    user = await UserModel.first()
    user.profile = await request.json()
    await user.save()

    return {"message": "Profile updated successfully"}

"""
Spaces
"""


@router.post("/spaces")
async def create_space(name: str = Body(...)):
    """Create a new space"""
    space = await SpaceModel.create(name=name)

    return await space.serialize()


@router.get("/spaces")
async def get_spaces(request: Request):
    """Get spaces"""
    spaces = await SpaceModel.filter(is_archived=False)

    serialized_spaces = []

    for space in spaces:
        serialized_space = await space.serialize()
        serialized_spaces.append(serialized_space)

    return serialized_spaces


@router.put("/spaces/{space_id}")
async def update_space(space_id: int, name: str = Body(...)):
    """Update a space"""
    space = await SpaceModel.get(id=space_id)

    if not space:
        return JSONResponse(status_code=404, content={"detail": "Space not found."})

    space.name = name
    await space.save()

    return JSONResponse(status_code=200, content={"detail": "Space name updated"})


@router.patch("/spaces/{space_id}")
async def archive_space(space_id: int):
    """Archive a space"""
    space = await SpaceModel.get_or_none(id=space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")

    space.is_archived = True
    await space.save()
    return {"detail": "Space archived"}


"""
Conversations
"""


@router.post("/spaces/{space_id}/conversations")
async def create_conversation(space_id: int):
    """Create a conversation"""
    space = await SpaceModel.get_or_none(id=space_id)

    preset = await PresetModel.filter(is_default=True).first()

    conversation = await ConversationModel.create(title="New Conversation", space=space, preset=preset, settings=preset.settings)

    for plugin in preset.plugins:
        plugin = await PluginRegistryModel.get_or_none(name=plugin['name'], is_active=True, is_internal=False)
        if plugin:
            await PluginInstanceModel.create(plugin=plugin, conversation=conversation)

    return await conversation.serialize()


@router.get("/conversations")
async def get_conversations():
    """Get all conversations"""
    conversations = await ConversationModel.filter(is_archived=False).order_by("-updated_at")

    serialized_conversations = [await conversation.serialize() for conversation in conversations]

    return serialized_conversations


@router.get("/conversations/settings")
async def get_settings_options():
    # TO-DO: Move these to config file
    options = {
        "llm": {
            "api_type": [
                {
                    "option": "Open AI",
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
                    "option": "gpt-3.5",
                    "value": "gpt-3.5"
                },
            ]
        }
    }

    return options


@router.get("/spaces/{space_id}/conversations")
async def get_conversations(request: Request, space_id: int = None):
    """Get conversations in space"""
    if space_id is None:
        return {"error": "Space ID is required"}

    conversations = await ConversationModel.filter(space_id=space_id, is_archived=False).order_by("-updated_at")
    serialized_conversations = [await conversation.serialize() for conversation in conversations]

    return serialized_conversations


@router.get("/conversations/{conversation_id}")
async def get_conversation(request: Request, conversation_id: int = None):
    """Get a single conversation"""
    conversation = await ConversationModel.get_or_none(id=conversation_id, is_archived=False)
    if conversation:
        return await conversation.serialize()
    else:
        print('Conversation not found!')


@router.patch("/conversations/{conversation_id}")
async def archive_conversation(conversation_id: int):
    """Archive a conversation"""

    conversation = await ConversationModel.get_or_none(id=conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Conversation not found")

    conversation.is_archived = True
    await conversation.save()
    return {"detail": "Conversation archived"}


@router.put("/conversations/{conversation_id}")
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
    new_plugin_names = None

    preset_data = conversation_data.get('preset')
    if preset_data:
        preset_id = preset_data.get('id')

        if preset_id != conversation.preset_id:
            preset = await PresetModel.get_or_none(id=preset_id)
            if not preset:
                raise HTTPException(status_code=404, detail="Preset not found")

            conversation.preset = preset
            conversation.settings=preset.settings
            # Update conversation settings with preset settings
            new_plugin_names = set(plugin['name'] for plugin in preset.plugins)

    # If no new plugins from preset, get from settings
    if new_plugin_names is None:
        new_plugin_names = set(
            plugin['name'] for plugin in conversation_data.get('plugins', []))

    current_plugins = [await plugin.serialize() for plugin in conversation.plugins if plugin.is_enabled]
    current_plugin_names = set(plugin['name'] for plugin in current_plugins)

    # Find plugins to add and remove
    plugins_to_add = new_plugin_names - current_plugin_names
    plugins_to_remove = current_plugin_names - new_plugin_names

    # Disable removed plugins
    for plugin_name in plugins_to_remove:
        plugin_instance = await PluginInstanceModel.get_or_none(conversation_id=conversation.id, plugin__name=plugin_name)
        if plugin_instance:
            plugin_instance.is_enabled = False
            await plugin_instance.save()

    # Enable active plugins
    for plugin_name in plugins_to_add:
        plugin_instance = await PluginInstanceModel.get_or_none(conversation_id=conversation.id, plugin__name=plugin_name)
        if plugin_instance:
            plugin_instance.is_enabled = True
            await plugin_instance.save()
        else:
            plugin = await PluginRegistryModel.get_or_none(name=plugin_name, is_active=True)
            if plugin:
                await PluginInstanceModel.create(conversation_id=conversation.id, plugin=plugin)

    # Save changes
    await conversation.save()

    output = await conversation.serialize()
    return output


@router.post("/presets/import")
async def add_presets(preset: dict = Body(...)):
    existing_preset = await PresetModel.get_or_none(name=preset['name'], is_active=False)

    if existing_preset:
        await existing_preset.delete()

    await PresetModel.create(**preset, is_custom=True)

    presets = await PresetModel.filter(is_active=True)

    return [preset.serialize() for preset in presets]

@router.post("/presets/{preset_id}")
async def delete_presets(preset_id: int):
    preset = await PresetModel.get_or_none(id=preset_id)

    if preset:
        # If the preset being deactivated is the default, set the first active preset as default
        if preset.is_default:
            first_active_preset = await PresetModel.filter(is_active=True).exclude(id=preset_id).first()
            if first_active_preset:
                first_active_preset.is_default = True
                await first_active_preset.save()

        preset.is_active = False
        preset.is_default = False
        await preset.save()

    presets = await PresetModel.filter(is_active=True)
    presets = [preset.serialize() for preset in presets]
    return presets


@router.get("/presets/{preset_id}/export")
async def export_preset(preset_id: int):
    preset = await PresetModel.get_or_none(id=preset_id)
    if preset is None:
        raise HTTPException(status_code=404, detail="Preset not found")

    preset_data = preset.serialize()
    
    del preset_data['is_custom']
    del preset_data['is_default']
    del preset_data['id']

    return preset_data


@router.put("/presets/{preset_id}")
async def update_preset(preset_id: int, preset_data: dict = Body(...)):
    preset_data = preset_data['preset']
    preset = await PresetModel.get_or_none(id=preset_id)
    if preset is None:
        raise HTTPException(status_code=404, detail="Preset not found")

    # If the updated preset is set to default, unset all other presets
    if preset_data['is_default']:
        await PresetModel.filter(is_default=True).update(is_default=False)

    preset.update_from_dict(preset_data)
    await preset.save()

    presets = await PresetModel.filter(is_active=True)
    presets = [preset.serialize() for preset in presets]
    return presets


@router.get("/presets")
async def get_presets():
    presets = await PresetModel.filter(is_active=True)
    presets = [preset.serialize() for preset in presets]
    return presets


@router.post("/presets")
async def create_preset(preset_name: str = Body(...), preset_description: str = Body(None), conversation_id: int = Body(...)):
    conversation = await ConversationModel.get_or_none(id=conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation_plugins = await conversation.plugins.all()
    serialized_plugins = [await plugin.serialize() for plugin in conversation_plugins]

    plugins = []

    for plugin in serialized_plugins:
        plugins.append({
            "name": plugin['name'],
            "settings": plugin['settings'],
            "data": None
        })

    preset = await PresetModel.create(
        name=preset_name,
        description=preset_description,
        plugins=plugins,
        settings=conversation.settings,
        is_custom=True,
        is_active=True,
        is_default=False
    )

    serialized = preset.serialize()

    return serialized


@router.get("/conversations/{conversation_id}/snippets")
async def get_snippets(conversation_id: int):
    plugins = await PluginRegistryModel.filter(plugin_type="snippet", is_active=True, is_internal=False)
    serialized = [plugin.serialize() for plugin in plugins]
    return serialized


@router.get("/conversations/{conversation_id}/tools")
async def get_tools(conversation_id: int):
    plugins = await PluginRegistryModel.filter(plugin_type="tool", is_active=True, is_internal=False)
    serialized = [plugin.serialize() for plugin in plugins]
    return serialized


@router.put("/integrations/{integration_id}")
async def disconnect_integration(integration_id: int):
    # Delete the instance
    integration_instance = await IntegrationInstanceModel.get_or_none(integration_id=integration_id)
    await integration_instance.delete()

    # Serialize all entries in the integration registry
    all_integrations = await IntegrationRegistryModel.all()
    serialized_integrations = [await integration.serialize() for integration in all_integrations]

    # Return the serialized integrations
    return serialized_integrations


@router.get("/integrations")
async def get_integrations():
    integrations = await IntegrationRegistryModel.filter()
    serialized = [await integration.serialize() for integration in integrations]
    return serialized


@router.post("/integrations")
async def new_integration(integration: dict = Body(...)):
    # Retrieve the existing integration from the database
    existing_integration = await IntegrationRegistryModel.get_or_none(id=integration['id'])

    # If the integration does not exist, return a 404 error
    if existing_integration is None:
        raise HTTPException(status_code=404, detail="Integration not found")

    # Check if an instance of the integration already exists
    existing_instance = await IntegrationInstanceModel.get_or_none(integration=existing_integration)

    if existing_instance:
        # If an instance already exists, update it
        existing_instance.credentials = {'api_key': integration['api_key']}
        await existing_instance.save()
    else:
        # If no instance exists, create a new one
        new_instance = IntegrationInstanceModel(
            integration=existing_integration,
            credentials={'api_key': integration['api_key']}
        )
        await new_instance.save()

    # Serialize all entries in the integration registry
    all_integrations = await IntegrationRegistryModel.all()
    serialized_integrations = [await integration.serialize() for integration in all_integrations]

    # Return the serialized integrations
    return serialized_integrations

@router.get("/plugins/{plugin_id}")
async def get_plugin_instance(plugin_id: int):
    plugin = await PluginInstanceModel.get_or_none(id=plugin_id)

    if plugin:
        plugin_data = await plugin.serialize()
    
    return plugin_data

@router.put("/plugins/{plugin_id}")
async def update_plugin_instance(plugin_id: int, settings: dict = Body(...)):
    plugin = await PluginInstanceModel.get_or_none(id=plugin_id)
    print('Updating settings: ', settings)
    plugin.settings = settings
    await plugin.save()

    return {"detail": "success"}

@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(request: Request, conversation_id: int, archived: Optional[bool] = False):
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


@router.post("/conversations/{conversation_id}/messages/archive")
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


@router.patch("/messages/{message_id}")
async def archive_message(message_id: int):
    """Archive a conversation"""

    message = await MessageModel.get_or_none(id=message_id)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Message not found")

    message.is_archived = True
    await message.save()
    return {"detail": "Message archived"}


@router.get("/conversations/{conversation_id}/export")
async def export_conversation_data(conversation_id: int, export_format: str = 'txt'):
    """Export a conversation's messages in plain text or JSON format"""
    exported_data = await export_conversation(conversation_id, export_format)

    file_name = f"conversation_{conversation_id}"
    file_name += ".txt" if export_format == "txt" else ".json"

    with open(file_name, "w") as f:
        f.write(exported_data)

    return FileResponse(file_name, media_type="application/octet-stream", filename=file_name)


@router.get("/conversations/{conversation_id}/documents")
async def get_documents(conversation_id: int):
    """Get a conversation's documents"""
    document_manager = DocumentManager(conversation_id)
    documents = await document_manager.get_documents(conversation_only=False)

    return JSONResponse(content=documents)


"""
Documents
"""


@router.patch("/documents/{doc_key}/conversations/{conversation_id}")
async def manage_conversation_id(doc_key: str, conversation_id: int, action: str = Body(...)):
    """ Add or remove a conversation from a document """
    document_manager = DocumentManager(conversation_id)
    if action == 'add':
        await document_manager.add_conversation_id(doc_key, conversation_id)
    else:
        await document_manager.remove_conversation_id(doc_key, conversation_id)

    return JSONResponse(content={"status": "success"})


@router.delete("/documents/{doc_key}")
async def delete_document(doc_key: str):
    """ Delete a document """
    conversation = await ConversationModel.first()
    document_manager = DocumentManager(conversation.id)
    await document_manager.delete_documents(doc_key)

    return JSONResponse(content={"status": "success"})


@router.post("/conversations/{conversation_id}/documents/add_file")
async def upload_document(conversation_id: int, file: UploadFile = File(...)):
    """ Create a new document from a file """
    document_manager = DocumentManager(conversation_id)
    try:
        await document_manager.load_files([file])
        return JSONResponse(status_code=200, content={"detail": "success"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/conversations/{conversation_id}/documents/add_url")
async def upload_url(conversation_id: int, url: str = Body(...)):
    """ Create a new document from a URL """
    document_manager = DocumentManager(conversation_id)
    await document_manager.load_urls([url])

    return JSONResponse(status_code=200, content={"detail": "success"})


"""
State
"""


@router.get("/state")
async def get_state(request: Request):
    """Get app state & initial data"""
    try:
        current_user = await get_current_user(request)
        state_data = current_user.app_state
        state_data["profile"] = current_user.profile
        return state_data
    except:
        return None


@router.post("/state")
async def save_state(request: Request):
    """Save app state"""
    current_user = await get_current_user(request)
    state_data = await request.json()
    current_user.app_state = state_data
    await current_user.save()

    return JSONResponse(status_code=200, content={"detail": "success"})

"""
Misc. routes
"""


@router.get("/initialize")
async def get_initial_data(request: Request):
    current_user = await get_current_user(request)

    # Get user data
    app_state = current_user.app_state
    user_profile = current_user.profile

    # Get spaces
    spaces = await SpaceModel.filter(is_archived=False)
    serialized_spaces = []
    for space in spaces:
        serialized_spaces.append(await space.serialize())

    # Get conversations
    conversations = await ConversationModel.filter(is_archived=False)
    serialized_conversations = []
    for conversation in conversations:
        serialized_conversations.append(await conversation.serialize())

    # Setup welcome conversation if first run
    if not app_state and not serialized_spaces and not serialized_conversations:

        preset = await PresetModel.filter(is_default=True).first()
        conversation = await ConversationModel.create(title="Welcome to Neary!", space=None, preset=preset, settings=preset.settings)

        for plugin in preset.plugins:
            plugin = await PluginRegistryModel.get_or_none(name=plugin['name'], is_active=True, is_internal=False)
            if plugin:
                await PluginInstanceModel.create(plugin=plugin, conversation=conversation)

        await MessageModel.create(conversation=conversation, role="assistant", content="Welcome to Neary! I'm here to help you get started. 🤗\n\nCan I have your name and your location, if you're comfortable sharing? I can use your location to set your timezone.")

        serialized_conversations.append(await conversation.serialize())

    initial_data = {
        'app_state': app_state,
        'user_profile': user_profile,
        'spaces': serialized_spaces,
        'conversations': serialized_conversations
    }

    return initial_data


@router.post("/action/response")
async def action_response(payload: dict):
    name = payload.get("name")
    conversation_id = payload.get("conversation_id")
    message_id = payload.get("message_id")
    data = payload.get("data")

    conversation_model = await ConversationModel.get_or_none(id=conversation_id)
    serialized = await conversation_model.serialize()

    conversation = Conversation(id=serialized['id'],
                                title=serialized['title'],
                                settings=serialized['settings'],
                                plugins=serialized['plugins'])

    await conversation.load_plugins()

    try:
        result = await conversation.handle_action(name, data, message_id)
        return JSONResponse(content={"detail": result})
    except Exception as e:
        print(e)
        return JSONResponse(content={"detail": "An error occured"})

"""
OAuth authentication routes
"""


@router.get("/start_oauth/{integration_id}")
async def start_oauth(integration_id: int):
    integration = await IntegrationRegistryModel.get(id=integration_id)

    if integration.auth_method != "oauth":
        raise HTTPException(
            status_code=400, detail="This integration does not use OAuth.")

    oauth_handler = OAuthHandler(integration)
    auth_url = oauth_handler.get_auth_url()
    return {"auth_url": auth_url}


@router.get("/oauth2/callback")
async def oauth_callback(request: Request):
    # Get the full URL that the user was redirected back to
    full_url = str(request.url)

    # Get the integration from the state parameter
    state = request.query_params.get("state")
    state_data = json.loads(state)
    csrf_token = state_data['csrf_token']
    integration_id = state_data['integration_id']
    integration = await IntegrationRegistryModel.get(id=integration_id)

    # Use the OAuthHandler to fetch the token
    oauth_handler = OAuthHandler(integration)
    token = oauth_handler.fetch_token(full_url)

    instance = await IntegrationInstanceModel.get_or_none(integration_id=integration_id)

    if instance is None:
        await IntegrationInstanceModel.create(integration=integration, credentials=token)
    else:
        instance.credentials = token
        await instance.save()

    # Redirect the user to a frontend route
    base_url = os.environ.get("BASE_URL", "http://localhost:3000")
    return RedirectResponse(url=base_url, status_code=302)


@router.get("/files/{plugin}/{filename}")
async def serve_file(plugin: str, filename: str):
    base_directory = Path(__file__).resolve().parent.parent / 'data' / 'files'
    file_path = base_directory / plugin / filename
    return FileResponse(str(file_path))
