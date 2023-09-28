from sqlalchemy.orm import Session
from backend import models

def create_message(db: Session, role: str, content: str, conversation_id: int, 
                   actions=None, metadata=None):
    message = models.MessageModel(role=role, content=content, 
                                  conversation_id=conversation_id, 
                                  actions=actions, metadata=metadata)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_message_by_id(db: Session, message_id: int):
    return db.query(models.MessageModel).filter(models.MessageModel.id == message_id).first()

def delete_message(db: Session, message: models.MessageModel):
    db.delete(message)
    db.commit()

def archive_message(db: Session, message: models.MessageModel):
    message.is_archived = True
    db.commit()

def get_messages_by_conversation_id(db: Session, conversation_id: int):
    return db.query(models.MessageModel).filter(models.MessageModel.conversation_id == conversation_id).order_by(models.MessageModel.created_at).all()