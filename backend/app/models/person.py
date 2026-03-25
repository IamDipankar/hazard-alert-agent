"""Person model — represents a household member from the imported spreadsheet."""

import uuid
from datetime import datetime
from sqlalchemy import String, Float, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class Person(Base):
    __tablename__ = "people"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_person_id: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Location
    district: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    upazila: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    union_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    village: Mapped[str | None] = mapped_column(String(200), nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Pre-known profile
    housing_type_known: Mapped[str | None] = mapped_column(String(50), nullable=True)
    livelihood_known: Mapped[str | None] = mapped_column(String(100), nullable=True)
    vulnerable_members_known: Mapped[str | None] = mapped_column(Text, nullable=True)
    water_source_known: Mapped[str | None] = mapped_column(String(100), nullable=True)
    latrine_type_known: Mapped[str | None] = mapped_column(String(100), nullable=True)
    income_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    family_size: Mapped[int | None] = mapped_column(nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
