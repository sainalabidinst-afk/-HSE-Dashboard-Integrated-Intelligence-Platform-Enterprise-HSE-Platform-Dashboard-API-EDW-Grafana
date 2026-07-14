"""
AI Safety Assistant repositories.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import uuid

from app.models.ai import AIDocument, AIDocumentChunk, AIConversation, AIMessage


class AIRepository:
    """Repository for AI Safety Assistant operations."""

    def __init__(self, db: Session):
        self.db = db

    # =============================================
    # DOCUMENT MANAGEMENT
    # =============================================

    def create_document(self, data: Dict) -> AIDocument:
        """Create a new knowledge base document."""
        doc = AIDocument(
            document_id=data.get("document_id") or str(uuid.uuid4()),
            title=data["title"],
            description=data.get("description"),
            document_type=data["document_type"],
            source_system=data.get("source_system"),
            source_id=data.get("source_id"),
            file_name=data.get("file_name"),
            file_path=data.get("file_path"),
            mime_type=data.get("mime_type"),
            file_size=data.get("file_size"),
            page_count=data.get("page_count"),
            language=data.get("language", "id"),
            metadata_=data.get("metadata_") or {},
            is_active=data.get("is_active", True),
            created_by=data.get("created_by"),
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_document(self, document_id: str) -> Optional[AIDocument]:
        """Get document by ID."""
        return self.db.query(AIDocument).filter(AIDocument.document_id == document_id).first()

    def get_documents(self, document_type: Optional[str] = None, source_system: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get documents with optional filters."""
        query = self.db.query(AIDocument)
        if document_type:
            query = query.filter(AIDocument.document_type == document_type)
        if source_system:
            query = query.filter(AIDocument.source_system == source_system)
        results = query.filter(AIDocument.is_active == True).order_by(desc(AIDocument.created_at)).limit(limit).all()
        return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in results]

    def delete_document(self, document_id: str) -> bool:
        """Soft delete a document."""
        doc = self.get_document(document_id)
        if doc:
            doc.is_active = False
            self.db.commit()
            return True
        return False

    # =============================================
    # CHUNK MANAGEMENT
    # =============================================

    def create_chunk(self, data: Dict) -> AIDocumentChunk:
        """Create a document chunk with embedding."""
        chunk = AIDocumentChunk(
            chunk_id=data.get("chunk_id") or str(uuid.uuid4()),
            document_id=data["document_id"],
            chunk_index=data["chunk_index"],
            text=data["text"],
            tokens=data.get("tokens"),
            embedding=data.get("embedding"),
            embedding_model=data.get("embedding_model"),
            metadata_=data.get("metadata_") or {},
        )
        self.db.add(chunk)
        self.db.commit()
        self.db.refresh(chunk)
        return chunk

    def get_chunks_by_document(self, document_id: str) -> List[Dict]:
        """Get all chunks for a document."""
        chunks = self.db.query(AIDocumentChunk).filter(
            AIDocumentChunk.document_id == document_id
        ).order_by(AIDocumentChunk.chunk_index).all()
        return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in chunks]

    def search_similar_chunks(self, query_embedding: List[float], top_k: int = 5, document_type: Optional[str] = None) -> List[Dict]:
        """Search for similar chunks using cosine similarity (pgvector)."""
        # For PostgreSQL with pgvector
        # This uses the <=> operator for cosine distance
        query = self.db.query(
            AIDocumentChunk,
            AIDocument.title,
            AIDocument.document_type,
            func.cosine_distance(AIDocumentChunk.embedding, str(query_embedding)).label("distance")
        ).join(AIDocument, AIDocumentChunk.document_id == AIDocument.document_id)

        if document_type:
            query = query.filter(AIDocument.document_type == document_type)

        results = query.filter(
            AIDocumentChunk.embedding.is_not(None)
        ).order_by(
            func.cosine_distance(AIDocumentChunk.embedding, str(query_embedding))
        ).limit(top_k).all()

        return [
            {
                "chunk_id": r[0].chunk_id,
                "document_id": r[0].document_id,
                "chunk_index": r[0].chunk_index,
                "text": r[0].text,
                "title": r[1],
                "document_type": r[2],
                "relevance_score": 1.0 - float(r[3]) if r[3] else 0.0,
            }
            for r in results
        ]

    # =============================================
    # CONVERSATION MANAGEMENT
    # =============================================

    def create_conversation(self, data: Dict) -> AIConversation:
        """Create a new conversation."""
        conv = AIConversation(
            conversation_id=data.get("conversation_id") or str(uuid.uuid4()),
            user_id=data.get("user_id"),
            title=data.get("title"),
            context_type=data.get("context_type"),
            context_id=data.get("context_id"),
        )
        self.db.add(conv)
        self.db.commit()
        self.db.refresh(conv)
        return conv

    def get_conversation(self, conversation_id: str) -> Optional[AIConversation]:
        """Get conversation by ID."""
        return self.db.query(AIConversation).filter(AIConversation.conversation_id == conversation_id).first()

    def get_user_conversations(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get conversations for a user."""
        conversations = self.db.query(AIConversation).filter(
            AIConversation.user_id == user_id
        ).order_by(desc(AIConversation.updated_at)).limit(limit).all()
        return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in conversations]

    # =============================================
    # MESSAGE MANAGEMENT
    # =============================================

    def create_message(self, data: Dict) -> AIMessage:
        """Create a message in a conversation."""
        msg = AIMessage(
            message_id=data.get("message_id") or str(uuid.uuid4()),
            conversation_id=data["conversation_id"],
            role=data["role"],
            content=data["content"],
            sources=data.get("sources"),
            confidence=data.get("confidence"),
            tokens_used=data.get("tokens_used"),
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_conversation_messages(self, conversation_id: str, limit: int = 50) -> List[Dict]:
        """Get messages for a conversation."""
        messages = self.db.query(AIMessage).filter(
            AIMessage.conversation_id == conversation_id
        ).order_by(AIMessage.created_at).limit(limit).all()
        return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in messages]

    def get_recent_messages(self, conversation_id: str, limit: int = 10) -> List[Dict]:
        """Get recent messages for context."""
        messages = self.db.query(AIMessage).filter(
            AIMessage.conversation_id == conversation_id
        ).order_by(desc(AIMessage.created_at)).limit(limit).all()
        return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in reversed(messages)]
