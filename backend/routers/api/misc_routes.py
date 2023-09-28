import json
from pathlib import Path

from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request, APIRouter, Depends
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse

from backend.database import get_db
from backend.auth import get_current_user
from backend.config import settings
from backend.models import *
from backend.conversation import Conversation
from backend.services.oauth_handler import OAuthHandler
from backend.services import user_service, space_service, conversation_service, preset_service, plugin_service, integration_service

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
async def save_state(request: Request, db: Session = Depends(get_db)):
    """Save app state"""
    current_user = get_current_user(request, db)
    user_data = {'app_state': await request.json()}
    user_service.update_user(db, current_user, user_data)

    return JSONResponse(status_code=200, content={"detail": "success"})

"""
Misc. routes
"""


@router.get("/initialize")
async def get_initial_data(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)

    # Get user data
    app_state = current_user.app_state
    user_profile = current_user.profile

    # Get spaces
    spaces = space_service.get_active_spaces(db)
    serialized_spaces = []
    for space in spaces:
        serialized_spaces.append(space.serialize())

    # Get conversations
    conversations = conversation_service.get_active_conversations(db)
    serialized_conversations = []
    for conversation in conversations:
        serialized_conversations.append(conversation.serialize())

    # Setup welcome conversation if first run
    if not app_state and not serialized_spaces and not serialized_conversations:
        conversation = conversation_service.create_conversation(db, space_id=None, title="New Conversation")

        serialized_conversations.append(conversation.serialize())

    # Get presets
    presets = preset_service.get_active_presets(db)
    presets = [preset.serialize() for preset in presets]

    # Get plugins
    plugins = plugin_service.get_active_plugins(db)
    plugins = [plugin.serialize() for plugin in plugins]

    # Get integrations
    integrations = integration_service.get_integrations(db)
    integrations = [integration.serialize() for integration in integrations]

    initial_data = {
        'app_state': app_state,
        'user_profile': user_profile,
        'spaces': serialized_spaces,
        'conversations': serialized_conversations,
        'plugins': plugins,
        'presets': presets,
        'integrations': integrations
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


@router.get("/files/{conversation_id}/{filename}")
async def serve_file(conversation_id: int, filename: str):
    base_directory = Path(__file__).resolve(
    ).parent.parent.parent / 'data' / 'files'
    file_path = base_directory / str(conversation_id) / filename
    return FileResponse(str(file_path), headers={"Content-Disposition": f"attachment; filename={filename}"})
