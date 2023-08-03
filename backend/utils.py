import json
from typing import Optional

from backend.conversation import Conversation
from backend.services.message_handler import MessageHandler
from backend.models import ConversationModel, ProgramRegistryModel

async def init_programs():
    """
    Adds programs to database, and updates instances if they already exist
    """
    with open('programs/registry.json', 'r') as f:
        programs = json.load(f)
        
    for program in programs:
        program_model = await ProgramRegistryModel.get_or_none(class_name=program["class_name"])
        if program_model:
            for key, value in program.items():
                setattr(program_model, key, value)
            await program_model.save()
        else:
            await ProgramRegistryModel.create(**program)

async def export_conversation(conversation_id: int, export_format: str = 'plain'):
    conversation = await ConversationModel.get(id=conversation_id).prefetch_related("messages")
    messages = await conversation.messages.all().order_by("created_at")

    if export_format == 'plain':
        result = ""
        for message in messages:
            sender = "Assistant" if message.role == "assistant" else "User"
            result += f"[{message.created_at.isoformat()}] {sender}: {message.content}\n"
        return result.rstrip()

    elif export_format == 'json':
        result = []
        for message in messages:
            sender = "Assistant" if message.role == "assistant" else "User"
            result.append({
                "created_at": message.created_at.isoformat(),
                "sender": sender,
                "content": message.content
            })
        return json.dumps(result)

    else:
        raise ValueError("Invalid export format. Choose either 'plain' or 'json'.")

async def get_conversation_instance(conversation_id: int, 
    message_handler: Optional[MessageHandler] = None) -> Conversation:
    
    if message_handler is None:
        message_handler = MessageHandler()

    conversation_model = await ConversationModel.get_or_none(id=conversation_id)
    conversation_data = await conversation_model.serialize() if conversation_model else None
    conversation = await Conversation.from_json(conversation_data, message_handler) if conversation_data else None

    return conversation