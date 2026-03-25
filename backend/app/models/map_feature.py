"""MapFeature model — GeoJSON features for the vulnerability map."""

import uuid
from datetime import datetime
from sqlalchemy import String, Float, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class MapFeature(Base):
    __tablename__ = "map_features"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("people.id"), nullable=True)
    call_session_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("call_sessions.id"), nullable=True)

    # Geometry stored as lat/lng since we don't need PostGIS
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)

    priority_class: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    layer_flags_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    popup_summary_bn: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Derived data for fast map rendering
    person_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    upazila: Mapped[str | None] = mapped_column(String(100), nullable=True)
    union_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    village: Mapped[str | None] = mapped_column(String(200), nullable=True)
    housing_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    livelihood: Mapped[str | None] = mapped_column(String(100), nullable=True)
    can_evacuate: Mapped[str | None] = mapped_column(String(30), nullable=True)
    vulnerable_members: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommended_followup: Mapped[str | None] = mapped_column(String(100), nullable=True)
    estimated_damage_bdt: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_salvageable_bdt: Mapped[float | None] = mapped_column(Float, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
