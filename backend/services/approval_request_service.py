from sqlalchemy.orm import Session
from backend import models

def create_approval_request(db: Session, conversation_id: int, tool_name: str, tool_args: dict):
    approval_request = models.ApprovalRequestModel(
        conversation_id=conversation_id, tool_name=tool_name, tool_args=tool_args)
    db.add(approval_request)
    db.commit()
    db.refresh(approval_request)
    return approval_request

def get_approval_request(db: Session, request_id: str, status: str):
    return db.query(models.ApprovalRequestModel).filter(
        models.ApprovalRequestModel.id == request_id, 
        models.ApprovalRequestModel.status == status
    ).first()

def update_approval_request_status(db: Session, approval_request: models.ApprovalRequestModel, status: str):
    approval_request.status = status
    db.commit()
    return approval_request