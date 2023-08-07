import os
from typing import Optional
from datetime import datetime

from fastapi import HTTPException, status, Request, APIRouter, Body, UploadFile, File
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from google_auth_oauthlib.flow import Flow

from backend.models import *
from backend.auth import get_current_user
from backend.utils import init_programs, get_conversation_instance, export_conversation
from backend.programs.calendar_chat.utils import GoogleService
from backend.services.message_handler import MessageHandler
from backend.services.documents.document_manager import DocumentManager
from backend.conversation import Conversation

router = APIRouter()

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
    """Create a conversation in a space"""

    space = await SpaceModel.get_or_none(id=space_id)

    program_registry = await ProgramRegistryModel.get(class_name="DefaultProgram")
    program = await ProgramModel.create(program_info=program_registry)

    conversation = await ConversationModel.create(space=space, program=program)
    conversation_data = await conversation.serialize()
    conversation_instance = await Conversation.from_json(conversation_data, MessageHandler())

    program.state = conversation_instance.program.get_program_data()
    program.settings = conversation_instance.program.get_settings()
    await program.save()

    return await conversation.serialize()

@router.post("/conversations")
async def create_conversation_without_space():
    """Create a conversation without a space"""

    program_registry = await ProgramRegistryModel.get(class_name="DefaultProgram")
    program = await ProgramModel.create(program_info=program_registry)

    conversation = await ConversationModel.create(program=program)
    conversation_data = await conversation.serialize()
    conversation_instance = await Conversation.from_json(conversation_data, MessageHandler())

    program.state = conversation_instance.program.get_program_data()
    program.settings = conversation_instance.program.get_settings()
    await program.save()

    return await conversation.serialize()

@router.get("/conversations")
async def get_conversations():
    """Get all conversations"""
    conversations = await ConversationModel.filter(is_archived=False).order_by("-updated_at")
    
    serialized_conversations = [await conversation.serialize() for conversation in conversations]

    return serialized_conversations


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


@router.get("/conversations/{conversation_id}/settings")
async def get_conversation_settings(request: Request, conversation_id: int):
    """Get a conversation's settings"""
    conversation = await get_conversation_instance(conversation_id)
    settings = await conversation.get_settings()

    return JSONResponse(content=settings)


@router.put("/conversations/{conversation_id}/settings")
async def update_conversation_settings(request: Request, conversation_id: int):
    """Update a conversation's settings"""
    settings = await request.json()

    conversation = await get_conversation_instance(conversation_id)
    await conversation.set_settings(settings)

    return JSONResponse(content={"detail": "Settings updated successfully"})


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
    conversation = await get_conversation_instance(conversation_id)
    documents = await conversation.document_manager.get_documents(
        conversation_only=False)

    return JSONResponse(content=documents)


"""
Documents
"""

@router.patch("/documents/{doc_key}/conversations/{conversation_id}")
async def manage_conversation_id(doc_key: str, conversation_id: int, action: str = Body(...)):
    """ Add or remove a conversation from a document """
    conversation = await get_conversation_instance(conversation_id)
    if action == 'add':
        await conversation.document_manager.add_conversation_id(doc_key, conversation_id)
    else:
        await conversation.document_manager.remove_conversation_id(doc_key, conversation_id)

    return JSONResponse(content={"status": "success"})


@router.delete("/documents/{doc_key}")
async def delete_document(doc_key: str):
    """ Delete a document """
    conversation_model = await ConversationModel.first()
    conversation_data = await conversation_model.serialize()
    if not conversation_data:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation = await Conversation.from_json(conversation_data, MessageHandler())
    await conversation.document_manager.delete_documents(doc_key)

    return JSONResponse(content={"status": "success"})


@router.post("/conversations/{conversation_id}/documents/add_file")
async def upload_document(conversation_id: int, file: UploadFile = File(...)):
    """ Create a new document from a file """
    try:
        conversation = await get_conversation_instance(conversation_id)
        dm = DocumentManager(conversation)
        
        await dm.load_files([file])

        return JSONResponse(status_code=200, content={"detail": "success"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/conversations/{conversation_id}/documents/add_url")
async def upload_url(conversation_id: int, url: str = Body(...)):
    """ Create a new document from a URL """
    conversation = await get_conversation_instance(conversation_id)
    dm = DocumentManager(conversation)
    await dm.load_urls([url])

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

    # Populate programs from registry
    await init_programs()

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
        program_info = await ProgramRegistryModel.get(class_name="SupportChat")
        program = await ProgramModel.create(program_info=program_info)

        conversation = await ConversationModel.create(program=program, title="Welcome to Neary!")
        
        await MessageModel.create(conversation=conversation, role="assistant", content="Welcome to Neary! I'm here to help you get started. 🤗\n\nCan I have your name and your location, if you're comfortable sharing? I can use your location to set your timezone.")
        
        conversation_data = await conversation.serialize()
        conversation_instance = await Conversation.from_json(conversation_data, MessageHandler())

        # Save initial program data & settings
        program.state = conversation_instance.program.get_program_data()
        program.settings = conversation_instance.program.get_settings()
        await program.save()

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

    conversation = await get_conversation_instance(conversation_id)

    try:
        result = await conversation.program.handle_action(name, data, message_id)
        return JSONResponse(content={"detail": result})
    except:
        # Raise a generic error for now
        return JSONResponse(content={"detail": "error"})

@router.get("/oauth2/callback")
async def oauth2_callback(request: Request, code=None):
    if not code:
        return {"error": "Authorization code is missing"}

    # Exchange the authorization code for an access token and a refresh token
    flow = Flow.from_client_secrets_file(
        'credentials/google_oauth.json', GoogleService.SCOPES)
    redirect_uri = os.environ.get("BASE_URL", "http://localhost:8000") + "/api/oauth2/callback"
    flow.redirect_uri = redirect_uri
    token = flow.fetch_token(code=code)

    # Save the new credentials in the AuthCredentialModel
    auth_data = {
        "access_token": token["access_token"],
        "refresh_token": token["refresh_token"],
        "expires_at": datetime.fromtimestamp(token["expires_at"]).isoformat(),
        "scopes": token["scope"],
    }

    auth_credential = AuthCredentialModel(
        provider="gmail",
        auth_type="oauth2",
        data=auth_data,
    )
    await auth_credential.save()
    base_url = os.environ.get("BASE_URL", "http://localhost:8000")
    return RedirectResponse(url=base_url, status_code=302)
