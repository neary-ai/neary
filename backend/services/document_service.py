from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from backend import models

def create_document(db: Session, metadata: dict, faiss_index: int):
    try:
        doc_chunk = db.add(models.DocumentModel(
            chunk_hash_id=metadata["id"],
            faiss_index=faiss_index,
            type=metadata["type"],
            collection=metadata["collection"],
            title=metadata["title"],
            content=metadata["content"],
            source=metadata["source"],
            document_key=metadata["document_key"]
        ))
        db.commit()
    except IntegrityError:
        print(
            f'Document with chunk_hash_id {metadata["id"]} already exists. Skipping.')
        db.rollback()
    return doc_chunk

def get_all_documents(db: Session):
    return db.query(models.DocumentModel).all()

def get_documents_by_faiss_indices(db: Session, faiss_indices: List[int], conversation_id: Optional[int] = None):
    base_query = db.query(models.DocumentModel).filter(models.DocumentModel.faiss_index.in_(faiss_indices))
    
    if conversation_id is not None:
        base_query = base_query.join(models.ConversationModel).filter(models.ConversationModel.id == conversation_id)
    
    return base_query.all()

def get_documents_by_key(db: Session, document_key):
    return db.query(models.DocumentModel).filter(models.DocumentModel.document_key == document_key).all()

def delete_documents_by_key(db: Session, document_key: str):
    documents = db.query(models.DocumentModel).filter(models.DocumentModel.document_key == document_key).all()
    for document in documents:
        db.delete(document)
    db.commit()