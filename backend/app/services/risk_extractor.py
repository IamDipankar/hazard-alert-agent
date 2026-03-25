"""
Risk extractor — extracts structured assessment from a completed call session.
Uses OpenAI structured outputs or falls back to heuristic extraction.
"""

import json
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.call_session import CallSession, CallTurn
from backend.app.models.person import Person
from backend.app.models.hazard_event import HazardEvent
from backend.app.models.extracted_assessment import ExtractedAssessment
from backend.app.models.followup import Followup
from backend.app.models.map_feature import MapFeature
from backend.app.config import settings

logger = logging.getLogger(__name__)

EXTRACTION_SCHEMA = {
    "call_status": "completed|partial|failed|callback",
    "warning_awareness": "yes|no|unsure",
    "district": "string",
    "upazila": "string",
    "union_name": "string",
    "village": "string",
    "housing_type": "jhupri|kacha|semi-pucca|pucca",
    "water_source_risk": "tube_well_protected|unprotected|contaminated|unknown",
    "latrine_risk": "stable|flood_prone|damaged|unknown",
    "livelihood": "fisherman|fish_farmer|farmer|salt_farmer|livestock_owner|other",
    "vulnerable_members": "comma-separated: elderly,disability,pregnancy,children,chronic_illness",
    "can_evacuate": "yes|no|with_assistance",
    "current_local_condition": "no_impact|water_rising|strong_wind|road_blocked|embankment_issue",
    "asset_at_risk": "comma-separated: livestock,nets,boat,seed,crop,documents,other",
    "priority_class": "low|medium|high|urgent",
    "recommended_followup": "human_callback|volunteer_referral|shelter_info|medical_support|none",
    "estimated_property_damage_risk_bdt": "number",
    "estimated_property_salvageable_bdt": "number",
    "damage_confidence": "0.0-1.0",
    "key_assets_named": "string",
    "evacuation_barrier_reason": "string",
    "medical_urgency": "none|low|medium|high|critical",
    "wash_urgency": "none|low|medium|high|critical",
    "transcript_summary_bn": "Bengali summary of the call",
    "agent_notes_internal_en": "English internal notes",
}


async def extract_from_session(
    session: CallSession,
    person: Optional[Person],
    event: Optional[HazardEvent],
    db: AsyncSession,
) -> Optional[ExtractedAssessment]:
    """Extract structured assessment from a completed call session."""

    transcript = session.transcript_text or ""

    extraction = None

    # Try OpenAI extraction
    if settings.OPENAI_API_KEY and transcript:
        try:
            extraction = await _openai_extract(transcript, person, event)
        except Exception as e:
            logger.error(f"OpenAI extraction failed: {e}")

    # Fallback to heuristic
    if not extraction:
        extraction = _heuristic_extract(person, event)

    # Save extracted assessment
    assessment = ExtractedAssessment(
        call_session_id=session.id,
        call_status=extraction.get("call_status", "completed"),
        warning_awareness=extraction.get("warning_awareness"),
        district=extraction.get("district") or (person.district if person else None),
        upazila=extraction.get("upazila") or (person.upazila if person else None),
        union_name=extraction.get("union_name") or (person.union_name if person else None),
        village=extraction.get("village") or (person.village if person else None),
        gps_lat=person.lat if person else None,
        gps_lng=person.lng if person else None,
        housing_type=extraction.get("housing_type") or (person.housing_type_known if person else None),
        water_source_risk=extraction.get("water_source_risk"),
        latrine_risk=extraction.get("latrine_risk"),
        livelihood=extraction.get("livelihood") or (person.livelihood_known if person else None),
        vulnerable_members=extraction.get("vulnerable_members") or (person.vulnerable_members_known if person else None),
        can_evacuate=extraction.get("can_evacuate"),
        current_local_condition=extraction.get("current_local_condition"),
        asset_at_risk=extraction.get("asset_at_risk"),
        priority_class=extraction.get("priority_class", "medium"),
        recommended_followup=extraction.get("recommended_followup", "none"),
        estimated_property_damage_risk_bdt=_safe_float(extraction.get("estimated_property_damage_risk_bdt")),
        estimated_property_salvageable_bdt=_safe_float(extraction.get("estimated_property_salvageable_bdt")),
        damage_confidence=_safe_float(extraction.get("damage_confidence")),
        key_assets_named=extraction.get("key_assets_named"),
        evacuation_barrier_reason=extraction.get("evacuation_barrier_reason"),
        medical_urgency=extraction.get("medical_urgency"),
        wash_urgency=extraction.get("wash_urgency"),
        transcript_summary_bn=extraction.get("transcript_summary_bn"),
        agent_notes_internal_en=extraction.get("agent_notes_internal_en"),
        support_priority_score=_calculate_priority_score(extraction),
        raw_extraction=extraction,
    )
    db.add(assessment)

    # Create followup if needed
    followup_type = extraction.get("recommended_followup", "none")
    if followup_type and followup_type != "none":
        followup = Followup(
            call_session_id=session.id,
            followup_type=followup_type,
            reason=extraction.get("agent_notes_internal_en", ""),
            status="pending",
        )
        db.add(followup)

    # Create map feature
    lat = person.lat if person and person.lat else 22.3 + (hash(str(session.id)) % 100) * 0.02
    lng = person.lng if person and person.lng else 89.5 + (hash(str(session.id)) % 100) * 0.02

    layer_flags = {
        "vulnerable": bool(extraction.get("vulnerable_members")),
        "wash_risk": extraction.get("wash_urgency") in ("high", "urgent", "critical"),
        "fragile_housing": extraction.get("housing_type") in ("jhupri", "kacha"),
        "evacuation_barrier": extraction.get("can_evacuate") in ("no", "with_assistance"),
        "livelihood_exposure": extraction.get("livelihood") in ("fisherman", "fish_farmer", "salt_farmer"),
        "urgent_callback": followup_type in ("human_callback", "medical_support"),
        "property_damage": bool(_safe_float(extraction.get("estimated_property_damage_risk_bdt"))),
        "salvage_opportunity": bool(_safe_float(extraction.get("estimated_property_salvageable_bdt"))),
    }

    map_feature = MapFeature(
        person_id=person.id if person else None,
        call_session_id=session.id,
        lat=lat,
        lng=lng,
        priority_class=extraction.get("priority_class", "medium"),
        layer_flags_json=layer_flags,
        popup_summary_bn=extraction.get("transcript_summary_bn", ""),
        person_name=person.name if person else "অজানা",
        district=extraction.get("district") or (person.district if person else None),
        upazila=extraction.get("upazila") or (person.upazila if person else None),
        union_name=extraction.get("union_name") or (person.union_name if person else None),
        village=extraction.get("village") or (person.village if person else None),
        housing_type=extraction.get("housing_type") or (person.housing_type_known if person else None),
        livelihood=extraction.get("livelihood") or (person.livelihood_known if person else None),
        can_evacuate=extraction.get("can_evacuate"),
        vulnerable_members=extraction.get("vulnerable_members") or (person.vulnerable_members_known if person else None),
        recommended_followup=followup_type,
        estimated_damage_bdt=_safe_float(extraction.get("estimated_property_damage_risk_bdt")),
        estimated_salvageable_bdt=_safe_float(extraction.get("estimated_property_salvageable_bdt")),
    )
    db.add(map_feature)

    await db.flush()
    return assessment


async def _openai_extract(transcript: str, person, event) -> dict:
    """Use OpenAI to extract structured data from conversation transcript."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    prompt = f"""Extract structured risk assessment data from this Bengali disaster call transcript.

Transcript:
{transcript}

Person Profile:
- Name: {person.name if person else 'Unknown'}
- District: {person.district if person else 'Unknown'}
- Known Housing: {person.housing_type_known if person else 'Unknown'}
- Known Livelihood: {person.livelihood_known if person else 'Unknown'}

Hazard Event:
- Type: {event.event_type if event else 'Unknown'}
- Severity: {event.severity if event else 'Unknown'}
- Lead Time: {event.lead_time_hours if event else 'Unknown'} hours

Extract all of these fields as JSON:
{json.dumps(EXTRACTION_SCHEMA, indent=2)}

Also estimate property damage and salvage potential in BDT based on:
- Housing type and hazard severity → damage risk
- Livelihood assets → asset value at risk
- Lead time and current actions → salvage potential
- Use conservative rough estimates appropriate for Bangladesh rural context

Respond with ONLY a JSON object containing all fields."""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1000,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)


def _heuristic_extract(person, event) -> dict:
    """Fallback heuristic extraction from person profile and event data."""

    housing = person.housing_type_known if person else "unknown"
    livelihood = person.livelihood_known if person else "unknown"
    vulnerable = person.vulnerable_members_known if person else None

    # Priority logic
    priority = "medium"
    if housing in ("jhupri", "kacha", "ঝুপড়ি", "কাঁচা"):
        priority = "high"
    if vulnerable:
        priority = "high"
    if event and event.severity in ("high", "extreme"):
        priority = "urgent" if priority == "high" else "high"

    # Damage estimation heuristic (BDT)
    damage_map = {
        "jhupri": 50000, "ঝুপড়ি": 50000,
        "kacha": 100000, "কাঁচা": 100000,
        "semi-pucca": 200000, "আধাপাকা": 200000,
        "pucca": 300000, "পাকা": 300000,
    }
    base_damage = damage_map.get(housing, 100000)

    severity_mult = {"low": 0.1, "medium": 0.3, "high": 0.6, "extreme": 0.9}
    mult = severity_mult.get(event.severity if event else "medium", 0.3)

    estimated_damage = base_damage * mult
    salvageable = estimated_damage * 0.3  # Assume 30% can be saved with action

    followup = "none"
    if priority == "urgent":
        followup = "human_callback"
    elif vulnerable:
        followup = "volunteer_referral"

    return {
        "call_status": "completed",
        "warning_awareness": "unsure",
        "district": person.district if person else None,
        "upazila": person.upazila if person else None,
        "union_name": person.union_name if person else None,
        "village": person.village if person else None,
        "housing_type": housing,
        "water_source_risk": "unknown",
        "latrine_risk": "unknown",
        "livelihood": livelihood,
        "vulnerable_members": vulnerable,
        "can_evacuate": "unsure",
        "current_local_condition": "unknown",
        "asset_at_risk": "",
        "priority_class": priority,
        "recommended_followup": followup,
        "estimated_property_damage_risk_bdt": estimated_damage,
        "estimated_property_salvageable_bdt": salvageable,
        "damage_confidence": 0.3,
        "key_assets_named": "",
        "evacuation_barrier_reason": "",
        "medical_urgency": "none",
        "wash_urgency": "none",
        "transcript_summary_bn": f"{person.name if person else 'ব্যক্তি'}-এর সাথে দুর্যোগ সতর্কতা কল সম্পন্ন হয়েছে।",
        "agent_notes_internal_en": f"Heuristic extraction - limited data. Priority: {priority}",
    }


def _calculate_priority_score(extraction: dict) -> float:
    """Calculate a 0-100 priority score from extracted data."""
    score = 20.0  # Base

    priority_map = {"low": 0, "medium": 20, "high": 40, "urgent": 60}
    score += priority_map.get(extraction.get("priority_class", "medium"), 20)

    if extraction.get("can_evacuate") in ("no",):
        score += 15
    if extraction.get("can_evacuate") in ("with_assistance",):
        score += 10

    if extraction.get("vulnerable_members"):
        score += 10

    if extraction.get("housing_type") in ("jhupri", "kacha", "ঝুপড়ি", "কাঁচা"):
        score += 10

    if extraction.get("medical_urgency") in ("high", "critical"):
        score += 15

    if extraction.get("wash_urgency") in ("high", "critical"):
        score += 10

    return min(score, 100.0)


def _safe_float(val) -> Optional[float]:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None
