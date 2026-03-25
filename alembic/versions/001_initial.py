"""Initial schema — all tables

Revision ID: 001_initial
Revises: None
Create Date: 2026-03-25
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ── people ──────────────────────────────────────────────────────
    op.create_table(
        "people",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("external_person_id", sa.String(100), unique=True, nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("district", sa.String(100), nullable=True, index=True),
        sa.Column("upazila", sa.String(100), nullable=True, index=True),
        sa.Column("union_name", sa.String(100), nullable=True),
        sa.Column("village", sa.String(200), nullable=True),
        sa.Column("lat", sa.Float, nullable=True),
        sa.Column("lng", sa.Float, nullable=True),
        sa.Column("housing_type_known", sa.String(50), nullable=True),
        sa.Column("livelihood_known", sa.String(100), nullable=True),
        sa.Column("vulnerable_members_known", sa.Text, nullable=True),
        sa.Column("water_source_known", sa.String(100), nullable=True),
        sa.Column("latrine_type_known", sa.String(100), nullable=True),
        sa.Column("income_level", sa.String(50), nullable=True),
        sa.Column("family_size", sa.Integer, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── hazard_events ───────────────────────────────────────────────
    op.create_table(
        "hazard_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_type", sa.String(50), nullable=False, index=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("severity", sa.String(50), nullable=False),
        sa.Column("official_signal", sa.String(100), nullable=True),
        sa.Column("lead_time_hours", sa.Float, nullable=True),
        sa.Column("source", sa.String(200), nullable=True),
        sa.Column("district_scope", sa.String(500), nullable=True),
        sa.Column("upazila_scope", sa.String(500), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("metadata_json", postgresql.JSONB, nullable=True),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── campaigns ───────────────────────────────────────────────────
    op.create_table(
        "campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("hazard_event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("hazard_events.id"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("status", sa.String(30), default="pending"),
        sa.Column("total_targets", sa.Integer, default=0),
        sa.Column("completed_calls", sa.Integer, default=0),
        sa.Column("failed_calls", sa.Integer, default=0),
        sa.Column("district_scope", sa.String(500), nullable=True),
        sa.Column("upazila_scope", sa.String(500), nullable=True),
        sa.Column("union_scope", sa.String(500), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── call_sessions ───────────────────────────────────────────────
    op.create_table(
        "call_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("campaigns.id"), nullable=True),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("people.id"), nullable=False),
        sa.Column("hazard_event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("hazard_events.id"), nullable=True),
        sa.Column("mode", sa.String(30), default="simulation"),
        sa.Column("status", sa.String(30), default="pending"),
        sa.Column("conversation_stage", sa.String(50), default="greeting"),
        sa.Column("urgency_level", sa.String(20), default="normal"),
        sa.Column("transcript_text", sa.Text, nullable=True),
        sa.Column("transcript_summary_bn", sa.Text, nullable=True),
        sa.Column("raw_asr_json", postgresql.JSONB, nullable=True),
        sa.Column("extraction_json", postgresql.JSONB, nullable=True),
        sa.Column("llm_trace_json", postgresql.JSONB, nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── call_turns ──────────────────────────────────────────────────
    op.create_table(
        "call_turns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("call_session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("call_sessions.id"), nullable=False),
        sa.Column("turn_number", sa.Integer, nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content_bn", sa.Text, nullable=True),
        sa.Column("content_en", sa.Text, nullable=True),
        sa.Column("audio_url", sa.String(500), nullable=True),
        sa.Column("asr_confidence", sa.Float, nullable=True),
        sa.Column("rag_context_used", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── extracted_assessments ───────────────────────────────────────
    op.create_table(
        "extracted_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("call_session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("call_sessions.id"), nullable=False, unique=True),
        sa.Column("call_status", sa.String(30), nullable=True),
        sa.Column("warning_awareness", sa.String(20), nullable=True),
        sa.Column("district", sa.String(100), nullable=True),
        sa.Column("upazila", sa.String(100), nullable=True),
        sa.Column("union_name", sa.String(100), nullable=True),
        sa.Column("village", sa.String(200), nullable=True),
        sa.Column("gps_lat", sa.Float, nullable=True),
        sa.Column("gps_lng", sa.Float, nullable=True),
        sa.Column("housing_type", sa.String(50), nullable=True),
        sa.Column("water_source_risk", sa.String(100), nullable=True),
        sa.Column("latrine_risk", sa.String(100), nullable=True),
        sa.Column("livelihood", sa.String(100), nullable=True),
        sa.Column("vulnerable_members", sa.Text, nullable=True),
        sa.Column("can_evacuate", sa.String(30), nullable=True),
        sa.Column("current_local_condition", sa.String(200), nullable=True),
        sa.Column("asset_at_risk", sa.Text, nullable=True),
        sa.Column("priority_class", sa.String(20), nullable=True, index=True),
        sa.Column("recommended_followup", sa.String(100), nullable=True),
        sa.Column("estimated_property_damage_risk_bdt", sa.Float, nullable=True),
        sa.Column("estimated_property_salvageable_bdt", sa.Float, nullable=True),
        sa.Column("damage_confidence", sa.Float, nullable=True),
        sa.Column("key_assets_named", sa.Text, nullable=True),
        sa.Column("evacuation_barrier_reason", sa.Text, nullable=True),
        sa.Column("medical_urgency", sa.String(50), nullable=True),
        sa.Column("wash_urgency", sa.String(50), nullable=True),
        sa.Column("transcript_summary_bn", sa.Text, nullable=True),
        sa.Column("agent_notes_internal_en", sa.Text, nullable=True),
        sa.Column("support_priority_score", sa.Float, nullable=True),
        sa.Column("raw_extraction", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── followups ───────────────────────────────────────────────────
    op.create_table(
        "followups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("call_session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("call_sessions.id"), nullable=False),
        sa.Column("followup_type", sa.String(50), nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("status", sa.String(30), default="pending"),
        sa.Column("assigned_to", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── map_features ────────────────────────────────────────────────
    op.create_table(
        "map_features",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("people.id"), nullable=True),
        sa.Column("call_session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("call_sessions.id"), nullable=True),
        sa.Column("lat", sa.Float, nullable=False),
        sa.Column("lng", sa.Float, nullable=False),
        sa.Column("priority_class", sa.String(20), nullable=True, index=True),
        sa.Column("layer_flags_json", postgresql.JSONB, nullable=True),
        sa.Column("popup_summary_bn", sa.Text, nullable=True),
        sa.Column("person_name", sa.String(255), nullable=True),
        sa.Column("district", sa.String(100), nullable=True),
        sa.Column("upazila", sa.String(100), nullable=True),
        sa.Column("union_name", sa.String(100), nullable=True),
        sa.Column("village", sa.String(200), nullable=True),
        sa.Column("housing_type", sa.String(50), nullable=True),
        sa.Column("livelihood", sa.String(100), nullable=True),
        sa.Column("can_evacuate", sa.String(30), nullable=True),
        sa.Column("vulnerable_members", sa.Text, nullable=True),
        sa.Column("recommended_followup", sa.String(100), nullable=True),
        sa.Column("estimated_damage_bdt", sa.Float, nullable=True),
        sa.Column("estimated_salvageable_bdt", sa.Float, nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── rag_documents ───────────────────────────────────────────────
    op.create_table(
        "rag_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("doc_type", sa.String(50), nullable=False),
        sa.Column("total_chunks", sa.Integer, default=0),
        sa.Column("metadata_json", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── rag_chunks ──────────────────────────────────────────────────
    op.create_table(
        "rag_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rag_documents.id"), nullable=False),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("heading", sa.String(500), nullable=True),
        sa.Column("word_count", sa.Integer, default=0),
        sa.Column("hazard_type", sa.String(50), nullable=True, index=True),
        sa.Column("phase", sa.String(30), nullable=True),
        sa.Column("action_priority", sa.String(30), nullable=True),
        sa.Column("housing_type", sa.String(50), nullable=True),
        sa.Column("livelihood", sa.String(100), nullable=True),
        sa.Column("vulnerability_group", sa.String(100), nullable=True),
        sa.Column("wash_asset", sa.String(100), nullable=True),
        sa.Column("lead_time_band", sa.String(50), nullable=True),
        sa.Column("signal_band", sa.String(50), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Add vector column separately using raw SQL for pgvector
    op.execute("ALTER TABLE rag_chunks ADD COLUMN IF NOT EXISTS embedding vector(1536)")

    # ── audit_logs ──────────────────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("action", sa.String(100), nullable=False, index=True),
        sa.Column("entity_type", sa.String(50), nullable=True),
        sa.Column("entity_id", sa.String(100), nullable=True),
        sa.Column("actor", sa.String(255), nullable=True),
        sa.Column("details", sa.Text, nullable=True),
        sa.Column("metadata_json", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("rag_chunks")
    op.drop_table("rag_documents")
    op.drop_table("map_features")
    op.drop_table("followups")
    op.drop_table("extracted_assessments")
    op.drop_table("call_turns")
    op.drop_table("call_sessions")
    op.drop_table("campaigns")
    op.drop_table("hazard_events")
    op.drop_table("people")
    op.execute("DROP EXTENSION IF EXISTS vector")
