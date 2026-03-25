"""Campaign model — a batch of outbound calls for a hazard event."""

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hazard_event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("hazard_events.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="pending")  # pending/active/completed/cancelled
    total_targets: Mapped[int] = mapped_column(Integer, default=0)
    completed_calls: Mapped[int] = mapped_column(Integer, default=0)
    failed_calls: Mapped[int] = mapped_column(Integer, default=0)
    district_scope: Mapped[str | None] = mapped_column(String(500), nullable=True)
    upazila_scope: Mapped[str | None] = mapped_column(String(500), nullable=True)
    union_scope: Mapped[str | None] = mapped_column(String(500), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
