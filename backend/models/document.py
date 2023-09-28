from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .conversation import conversation_document
from .base import Base

class DocumentModel(Base):
    __tablename__ = 'document_model'

    id = Column(Integer, primary_key=True)
    chunk_hash_id = Column(String, unique=True)
    faiss_index = Column(Integer)
    document_key = Column(String, nullable=True)
    content = Column(Text)
    type = Column(String, nullable=True)
    collection = Column(String, nullable=True)
    title = Column(String, nullable=True)
    source = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    meta_data = Column(JSON, nullable=True)

    # Relationship
    conversations = relationship('ConversationModel', secondary=conversation_document, back_populates='documents')

    def serialize(self):
        conversation_ids = [c.id for c in self.conversations]

        return {
            "id": self.id,
            "conversation_ids": conversation_ids,
            "chunk_hash_id": self.chunk_hash_id,
            "faiss_index": self.faiss_index,
            "document_key": self.document_key,
            "content": self.content,
            "type": self.type,
            "collection": self.collection,
            "title": self.title,
            "source": self.source,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.meta_data
        }
