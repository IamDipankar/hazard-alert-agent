"""HazardEvent model — represents a disaster alert event."""

import uuid
from datetime import datetime
from sqlalchemy import String, Float, Text, DateTime, Integer, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class HazardEvent(Base):
    __tablename__ = "hazard_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)  # low/medium/high/extreme
    official_signal: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lead_time_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str | None] = mapped_column(String(200), nullable=True)
    district_scope: Mapped[str | None] = mapped_column(String(500), nullable=True)
    upazila_scope: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
