import json

from sqlalchemy.orm import Session

from backend.services import message_service

def export_conversation(db: Session, conversation_id: int, export_format: str = 'plain'):
    messages = message_service.get_messages_by_conversation_id(db, conversation_id)

    file_name = f"conversation_{conversation_id}"
    file_name += ".txt" if export_format == "plain" else ".json"

    with open(file_name, "w") as f:
        if export_format == 'plain':
            result = ""
            for message in messages:
                sender = "Assistant" if message.role == "assistant" else "User"
                result += f"[{message.created_at.isoformat()}] {sender}: {message.content}\n"
            f.write(result.rstrip())

        elif export_format == 'json':
            result = []
            for message in messages:
                sender = "Assistant" if message.role == "assistant" else "User"
                result.append({
                    "created_at": message.created_at.isoformat(),
                    "sender": sender,
                    "content": message.content
                })
            f.write(json.dumps(result))

        else:
            raise ValueError("Invalid export format. Choose either 'plain' or 'json'.")

    return file_name