"""Followup model — actions needed after a call."""

import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class Followup(Base):
    __tablename__ = "followups"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("call_sessions.id"), nullable=False)
    followup_type: Mapped[str] = mapped_column(String(50), nullable=False)  # human_callback/volunteer_referral/shelter_info/medical_support/none
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="pending")  # pending/assigned/completed/cancelled
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
