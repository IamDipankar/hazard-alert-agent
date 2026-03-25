"""CallSession and CallTurn models — individual call records and conversation turns."""

import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class CallSession(Base):
    __tablename__ = "call_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    person_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("people.id"), nullable=False)
    hazard_event_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("hazard_events.id"), nullable=True)
    mode: Mapped[str] = mapped_column(String(30), default="simulation")  # simulation/live
    status: Mapped[str] = mapped_column(String(30), default="pending")  # pending/ringing/active/completed/failed
    conversation_stage: Mapped[str] = mapped_column(String(50), default="greeting")
    urgency_level: Mapped[str] = mapped_column(String(20), default="normal")  # normal/elevated/urgent/critical
    transcript_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcript_summary_bn: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_asr_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    extraction_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    llm_trace_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CallTurn(Base):
    __tablename__ = "call_turns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("call_sessions.id"), nullable=False)
    turn_number: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # agent/user
    content_bn: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    asr_confidence: Mapped[float | None] = mapped_column(nullable=True)
    rag_context_used: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
