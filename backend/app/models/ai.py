"""
SQLAlchemy Models for AI Safety Assistant and Knowledge Layer.
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float,
    ForeignKey, Index, TypeDecorator, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import json


class VectorType(TypeDecorator):
    """Custom type for pgvector - stores as JSON in SQLite, VECTOR in PostgreSQL."""
    impl = JSON
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, list):
            return value
        return list(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, list):
            return value
        return list(value)

from app.database import Base


class AIDocument(Base):
    """
    Knowledge base document (SOP, regulation, audit report, etc.).
    """
    __tablename__ = "ai_documents"
    __table_args__ = {"schema": "hse"}

    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    document_type = Column(String(50), nullable=False)  # sop, regulation, audit_report, incident_report, ptw, training, policy
    source_system = Column(String(100))  # manual_upload, etl, audit, incident
    source_id = Column(String(100))  # ID from source system (e.g., audit_id, incident_id)
    file_name = Column(String(500))
    file_path = Column(String(1000))
    mime_type = Column(String(100))
    file_size = Column(Integer)
    page_count = Column(Integer)
    language = Column(String(10), default="id")
    metadata_ = Column("metadata", JSON)  # author, version, effective_date, etc.
    is_active = Column(Boolean, default=True)
    created_by = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    indexed_at = Column(DateTime)
    embedding_model = Column(String(100))

    chunks = relationship("AIDocumentChunk", back_populates="document", cascade="all, delete-orphan")


class AIDocumentChunk(Base):
    """
    Text chunk from a document with embedding vector.
    """
    __tablename__ = "ai_document_chunks"
    __table_args__ = {"schema": "hse"}

    chunk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("hse.ai_documents.document_id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order within document
    text = Column(Text, nullable=False)
    tokens = Column(Integer)
    embedding = Column(VectorType)  # 1536 dimensions for OpenAI ada-002
    embedding_model = Column(String(100))
    metadata_ = Column("metadata", JSON)  # page_number, section, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("AIDocument", back_populates="chunks")


class AIConversation(Base):
    """
    AI Safety Assistant conversation session.
    """
    __tablename__ = "ai_conversations"
    __table_args__ = {"schema": "hse"}

    conversation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("hse.security_users.user_id", ondelete="SET NULL"))
    title = Column(String(500))
    context_type = Column(String(50))  # general, incident, audit, ptw, site
    context_id = Column(String(100))  # Related entity ID
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("AIMessage", back_populates="conversation", cascade="all, delete-orphan")


class AIMessage(Base):
    """
    Individual message in a conversation.
    """
    __tablename__ = "ai_messages"
    __table_args__ = {"schema": "hse"}

    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("hse.ai_conversations.conversation_id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    sources = Column(JSON)  # List of source documents used
    confidence = Column(Float)  # 0.0 - 1.0
    feedback = Column(String(20))  # helpful, not_helpful, inaccurate
    tokens_used = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("AIConversation", back_populates="messages")


# Indexes
Index("idx_ai_documents_type", AIDocument.document_type, AIDocument.is_active)
Index("idx_ai_documents_source", AIDocument.source_system, AIDocument.source_id)
Index("idx_ai_chunks_document", AIDocumentChunk.document_id)
Index("idx_ai_conversations_user", AIConversation.user_id, AIConversation.created_at)
Index("idx_ai_messages_conversation", AIMessage.conversation_id, AIMessage.created_at)
