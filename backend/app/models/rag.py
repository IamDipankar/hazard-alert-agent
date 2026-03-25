"""RAG models — documents and embedded chunks for retrieval."""

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from backend.app.database import Base


class RAGDocument(Base):
    __tablename__ = "rag_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(50), nullable=False)  # cyclone_rag/flood_rag/script
    total_chunks: Mapped[int] = mapped_column(Integer, default=0)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RAGChunk(Base):
    __tablename__ = "rag_chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rag_documents.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    heading: Mapped[str | None] = mapped_column(String(500), nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, default=0)

    # Metadata for retrieval filtering
    hazard_type: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    phase: Mapped[str | None] = mapped_column(String(30), nullable=True)  # before/during/after
    action_priority: Mapped[str | None] = mapped_column(String(30), nullable=True)
    housing_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    livelihood: Mapped[str | None] = mapped_column(String(100), nullable=True)
    vulnerability_group: Mapped[str | None] = mapped_column(String(100), nullable=True)
    wash_asset: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lead_time_band: Mapped[str | None] = mapped_column(String(50), nullable=True)
    signal_band: Mapped[str | None] = mapped_column(String(50), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # pgvector embedding
    embedding = mapped_column(Vector(1536), nullable=True)  # OpenAI text-embedding-3-small dimension

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
