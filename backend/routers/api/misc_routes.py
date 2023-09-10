import json
from pathlib import Path

from fastapi import HTTPException, status, Request, APIRouter
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse

from backend.auth import get_current_user
from backend.config import settings
from backend.models import *
from backend.conversation import Conversation
from backend.services.oauth_handler import OAuthHandler

router = APIRouter()

@router.put("/profile")
async def update_user_profile(request: Request):
    user = await UserModel.first()
    user.profile = await request.json()
    await user.save()

    return {"message": "Profile updated successfully"}

@router.patch("/messages/{message_id}")
async def archive_message(message_id: int):
    """Archive a message"""

    message = await MessageModel.get_or_none(id=message_id)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Message not found")

    message.is_archived = True
    await message.save()
    return {"detail": "Message archived"}

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
        conversation = await ConversationModel.create(title="New Conversation", space=None, preset=preset, settings=preset.settings)

        for plugin in preset.plugins:
            plugin_registry = await PluginRegistryModel.get_or_none(name=plugin["name"])
            if plugin_registry:
                plugin_registry.is_enabled = True
                await plugin_registry.save()
                await PluginInstanceModel.create(name=plugin["name"], plugin=plugin_registry, functions=plugin["functions"], settings=plugin.get("settings", None), conversation=conversation)
            else:
                print('Registry information not found for plugin: ', plugin["name"])
        
        serialized_conversations.append(await conversation.serialize())

    # Get presets
    presets = await PresetModel.filter(is_active=True)
    presets = [preset.serialize() for preset in presets]

    # Get plugins
    plugins = await PluginRegistryModel.all()
    plugins = [await plugin.serialize() for plugin in plugins]

    initial_data = {
        'app_state': app_state,
        'user_profile': user_profile,
        'spaces': serialized_spaces,
        'conversations': serialized_conversations,
        'plugins': plugins,
        'presets': presets
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
    base_url = settings.application.get("base_url", "http://localhost:8000")
    return RedirectResponse(url=base_url, status_code=302)


@router.get("/files/{plugin}/{filename}")
async def serve_file(plugin: str, filename: str):
    base_directory = Path(__file__).resolve().parent.parent / 'data' / 'files'
    file_path = base_directory / plugin / filename
    return FileResponse(str(file_path))
