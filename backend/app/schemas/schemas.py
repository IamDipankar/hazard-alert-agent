"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


# ── Person ──────────────────────────────────────────────────────────

class PersonOut(BaseModel):
    id: UUID
    external_person_id: Optional[str] = None
    name: str
    phone: Optional[str] = None
    gender: Optional[str] = None
    district: Optional[str] = None
    upazila: Optional[str] = None
    union_name: Optional[str] = None
    village: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    housing_type_known: Optional[str] = None
    livelihood_known: Optional[str] = None
    vulnerable_members_known: Optional[str] = None
    water_source_known: Optional[str] = None
    latrine_type_known: Optional[str] = None
    income_level: Optional[str] = None
    family_size: Optional[int] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class PersonFilter(BaseModel):
    district: Optional[str] = None
    upazila: Optional[str] = None
    union_name: Optional[str] = None
    housing_type: Optional[str] = None
    livelihood: Optional[str] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 50


# ── Hazard Event ────────────────────────────────────────────────────

class HazardEventCreate(BaseModel):
    event_type: str
    title: str
    severity: str = "high"
    official_signal: Optional[str] = None
    lead_time_hours: Optional[float] = None
    source: Optional[str] = None
    district_scope: Optional[str] = None
    upazila_scope: Optional[str] = None
    description: Optional[str] = None


class HazardEventOut(BaseModel):
    id: UUID
    event_type: str
    title: str
    severity: str
    official_signal: Optional[str] = None
    lead_time_hours: Optional[float] = None
    source: Optional[str] = None
    district_scope: Optional[str] = None
    upazila_scope: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Campaign ────────────────────────────────────────────────────────

class CampaignCreate(BaseModel):
    hazard_event_id: UUID
    title: str
    district_scope: Optional[str] = None
    upazila_scope: Optional[str] = None
    union_scope: Optional[str] = None


class CampaignOut(BaseModel):
    id: UUID
    hazard_event_id: UUID
    title: str
    status: str
    total_targets: int
    completed_calls: int
    failed_calls: int
    district_scope: Optional[str] = None
    upazila_scope: Optional[str] = None
    union_scope: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Call Session ────────────────────────────────────────────────────

class CallSessionCreate(BaseModel):
    person_id: UUID
    hazard_event_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None


class CallSessionOut(BaseModel):
    id: UUID
    campaign_id: Optional[UUID] = None
    person_id: UUID
    hazard_event_id: Optional[UUID] = None
    mode: str
    status: str
    conversation_stage: str
    urgency_level: str
    transcript_text: Optional[str] = None
    transcript_summary_bn: Optional[str] = None
    extraction_json: Optional[dict] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Call Turn ───────────────────────────────────────────────────────

class CallTurnOut(BaseModel):
    id: UUID
    call_session_id: UUID
    turn_number: int
    role: str
    content_bn: Optional[str] = None
    content_en: Optional[str] = None
    audio_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Chat message from client ───────────────────────────────────────

class ChatMessage(BaseModel):
    call_session_id: UUID
    text: Optional[str] = None
    audio_base64: Optional[str] = None


class ChatResponse(BaseModel):
    text_bn: str
    audio_url: Optional[str] = None
    stage: str
    urgency: str
    extraction_preview: Optional[dict] = None
    is_final: bool = False


# ── Extracted Assessment ────────────────────────────────────────────

class ExtractedAssessmentOut(BaseModel):
    id: UUID
    call_session_id: UUID
    call_status: Optional[str] = None
    warning_awareness: Optional[str] = None
    district: Optional[str] = None
    upazila: Optional[str] = None
    union_name: Optional[str] = None
    village: Optional[str] = None
    housing_type: Optional[str] = None
    water_source_risk: Optional[str] = None
    latrine_risk: Optional[str] = None
    livelihood: Optional[str] = None
    vulnerable_members: Optional[str] = None
    can_evacuate: Optional[str] = None
    current_local_condition: Optional[str] = None
    asset_at_risk: Optional[str] = None
    priority_class: Optional[str] = None
    recommended_followup: Optional[str] = None
    estimated_property_damage_risk_bdt: Optional[float] = None
    estimated_property_salvageable_bdt: Optional[float] = None
    damage_confidence: Optional[float] = None
    key_assets_named: Optional[str] = None
    evacuation_barrier_reason: Optional[str] = None
    medical_urgency: Optional[str] = None
    wash_urgency: Optional[str] = None
    transcript_summary_bn: Optional[str] = None
    agent_notes_internal_en: Optional[str] = None
    support_priority_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Analytics ───────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_people: int = 0
    total_campaigns: int = 0
    total_calls: int = 0
    completed_calls: int = 0
    failed_calls: int = 0
    active_calls: int = 0
    warning_awareness_rate: float = 0.0
    can_evacuate_rate: float = 0.0
    priority_distribution: dict = {}
    housing_distribution: dict = {}
    livelihood_distribution: dict = {}
    followup_distribution: dict = {}
    total_estimated_damage_bdt: float = 0.0
    total_salvageable_bdt: float = 0.0
    vulnerable_household_count: int = 0
    wash_risk_count: int = 0
    urgent_followup_count: int = 0


# ── Map ─────────────────────────────────────────────────────────────

class MapFeatureOut(BaseModel):
    id: UUID
    lat: float
    lng: float
    priority_class: Optional[str] = None
    person_name: Optional[str] = None
    district: Optional[str] = None
    upazila: Optional[str] = None
    union_name: Optional[str] = None
    village: Optional[str] = None
    housing_type: Optional[str] = None
    livelihood: Optional[str] = None
    can_evacuate: Optional[str] = None
    vulnerable_members: Optional[str] = None
    recommended_followup: Optional[str] = None
    estimated_damage_bdt: Optional[float] = None
    estimated_salvageable_bdt: Optional[float] = None
    popup_summary_bn: Optional[str] = None
    layer_flags_json: Optional[dict] = None

    class Config:
        from_attributes = True


class MapFilter(BaseModel):
    district: Optional[str] = None
    upazila: Optional[str] = None
    union_name: Optional[str] = None
    village: Optional[str] = None
    housing_type: Optional[str] = None
    livelihood: Optional[str] = None
    priority_class: Optional[str] = None
    followup_type: Optional[str] = None
    layer: Optional[str] = None  # vulnerable/wash_risk/fragile_housing/etc.
