"""Analytics and dashboard endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case

from backend.app.database import get_db
from backend.app.models.person import Person
from backend.app.models.campaign import Campaign
from backend.app.models.call_session import CallSession
from backend.app.models.extracted_assessment import ExtractedAssessment
from backend.app.models.followup import Followup
from backend.app.schemas.schemas import DashboardStats

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Aggregate dashboard stats across all data."""

    # Total people
    people_count = (await db.execute(select(func.count(Person.id)))).scalar() or 0

    # Total campaigns
    campaign_count = (await db.execute(select(func.count(Campaign.id)))).scalar() or 0

    # Call stats
    total_calls = (await db.execute(select(func.count(CallSession.id)))).scalar() or 0
    completed_calls = (await db.execute(
        select(func.count(CallSession.id)).where(CallSession.status == "completed")
    )).scalar() or 0
    failed_calls = (await db.execute(
        select(func.count(CallSession.id)).where(CallSession.status == "failed")
    )).scalar() or 0
    active_calls = (await db.execute(
        select(func.count(CallSession.id)).where(CallSession.status == "active")
    )).scalar() or 0

    # Assessment aggregations
    awareness_yes = (await db.execute(
        select(func.count(ExtractedAssessment.id))
        .where(ExtractedAssessment.warning_awareness == "yes")
    )).scalar() or 0

    total_assessed = (await db.execute(
        select(func.count(ExtractedAssessment.id))
        .where(ExtractedAssessment.warning_awareness.isnot(None))
    )).scalar() or 0

    awareness_rate = (awareness_yes / total_assessed * 100) if total_assessed > 0 else 0.0

    evac_yes = (await db.execute(
        select(func.count(ExtractedAssessment.id))
        .where(ExtractedAssessment.can_evacuate == "yes")
    )).scalar() or 0

    total_evac_asked = (await db.execute(
        select(func.count(ExtractedAssessment.id))
        .where(ExtractedAssessment.can_evacuate.isnot(None))
    )).scalar() or 0

    evac_rate = (evac_yes / total_evac_asked * 100) if total_evac_asked > 0 else 0.0

    # Priority distribution
    priority_result = await db.execute(
        select(ExtractedAssessment.priority_class, func.count(ExtractedAssessment.id))
        .where(ExtractedAssessment.priority_class.isnot(None))
        .group_by(ExtractedAssessment.priority_class)
    )
    priority_dist = {row[0]: row[1] for row in priority_result.all()}

    # Housing distribution
    housing_result = await db.execute(
        select(ExtractedAssessment.housing_type, func.count(ExtractedAssessment.id))
        .where(ExtractedAssessment.housing_type.isnot(None))
        .group_by(ExtractedAssessment.housing_type)
    )
    housing_dist = {row[0]: row[1] for row in housing_result.all()}

    # Livelihood distribution
    livelihood_result = await db.execute(
        select(ExtractedAssessment.livelihood, func.count(ExtractedAssessment.id))
        .where(ExtractedAssessment.livelihood.isnot(None))
        .group_by(ExtractedAssessment.livelihood)
    )
    livelihood_dist = {row[0]: row[1] for row in livelihood_result.all()}

    # Followup distribution
    followup_result = await db.execute(
        select(Followup.followup_type, func.count(Followup.id))
        .group_by(Followup.followup_type)
    )
    followup_dist = {row[0]: row[1] for row in followup_result.all()}

    # Damage totals
    damage_total = (await db.execute(
        select(func.coalesce(func.sum(ExtractedAssessment.estimated_property_damage_risk_bdt), 0))
    )).scalar() or 0.0

    salvage_total = (await db.execute(
        select(func.coalesce(func.sum(ExtractedAssessment.estimated_property_salvageable_bdt), 0))
    )).scalar() or 0.0

    # Vulnerable household count
    vulnerable_count = (await db.execute(
        select(func.count(ExtractedAssessment.id))
        .where(ExtractedAssessment.vulnerable_members.isnot(None))
        .where(ExtractedAssessment.vulnerable_members != "")
    )).scalar() or 0

    # WASH risk count
    wash_risk_count = (await db.execute(
        select(func.count(ExtractedAssessment.id))
        .where(ExtractedAssessment.wash_urgency.in_(["high", "urgent", "critical"]))
    )).scalar() or 0

    # Urgent followup
    urgent_followup = (await db.execute(
        select(func.count(ExtractedAssessment.id))
        .where(ExtractedAssessment.priority_class == "urgent")
    )).scalar() or 0

    return DashboardStats(
        total_people=people_count,
        total_campaigns=campaign_count,
        total_calls=total_calls,
        completed_calls=completed_calls,
        failed_calls=failed_calls,
        active_calls=active_calls,
        warning_awareness_rate=round(awareness_rate, 1),
        can_evacuate_rate=round(evac_rate, 1),
        priority_distribution=priority_dist,
        housing_distribution=housing_dist,
        livelihood_distribution=livelihood_dist,
        followup_distribution=followup_dist,
        total_estimated_damage_bdt=float(damage_total),
        total_salvageable_bdt=float(salvage_total),
        vulnerable_household_count=vulnerable_count,
        wash_risk_count=wash_risk_count,
        urgent_followup_count=urgent_followup,
    )
