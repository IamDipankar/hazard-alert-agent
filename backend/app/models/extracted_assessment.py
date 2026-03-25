"""ExtractedAssessment — structured data extracted from a completed call."""

import uuid
from datetime import datetime
from sqlalchemy import String, Float, Text, DateTime, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class ExtractedAssessment(Base):
    __tablename__ = "extracted_assessments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("call_sessions.id"), nullable=False, unique=True)

    # Core extraction fields
    call_status: Mapped[str | None] = mapped_column(String(30), nullable=True)  # completed/partial/failed/callback
    warning_awareness: Mapped[str | None] = mapped_column(String(20), nullable=True)  # yes/no/unsure
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    upazila: Mapped[str | None] = mapped_column(String(100), nullable=True)
    union_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    village: Mapped[str | None] = mapped_column(String(200), nullable=True)
    gps_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    gps_lng: Mapped[float | None] = mapped_column(Float, nullable=True)

    housing_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    water_source_risk: Mapped[str | None] = mapped_column(String(100), nullable=True)
    latrine_risk: Mapped[str | None] = mapped_column(String(100), nullable=True)
    livelihood: Mapped[str | None] = mapped_column(String(100), nullable=True)
    vulnerable_members: Mapped[str | None] = mapped_column(Text, nullable=True)  # comma-separated
    can_evacuate: Mapped[str | None] = mapped_column(String(30), nullable=True)
    current_local_condition: Mapped[str | None] = mapped_column(String(200), nullable=True)
    asset_at_risk: Mapped[str | None] = mapped_column(Text, nullable=True)

    priority_class: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    recommended_followup: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Damage estimation
    estimated_property_damage_risk_bdt: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_property_salvageable_bdt: Mapped[float | None] = mapped_column(Float, nullable=True)
    damage_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    key_assets_named: Mapped[str | None] = mapped_column(Text, nullable=True)
    evacuation_barrier_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    medical_urgency: Mapped[str | None] = mapped_column(String(50), nullable=True)
    wash_urgency: Mapped[str | None] = mapped_column(String(50), nullable=True)

    transcript_summary_bn: Mapped[str | None] = mapped_column(Text, nullable=True)
    agent_notes_internal_en: Mapped[str | None] = mapped_column(Text, nullable=True)

    support_priority_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_extraction: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
