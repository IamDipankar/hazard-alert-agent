"""Campaign management endpoints."""

from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.app.database import get_db
from backend.app.models.campaign import Campaign
from backend.app.models.person import Person
from backend.app.models.call_session import CallSession
from backend.app.schemas.schemas import CampaignCreate, CampaignOut

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=list[CampaignOut])
async def list_campaigns(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).order_by(Campaign.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=CampaignOut)
async def create_campaign(data: CampaignCreate, db: AsyncSession = Depends(get_db)):
    # Count target people in scope
    query = select(func.count(Person.id))
    if data.district_scope:
        query = query.where(Person.district == data.district_scope)
    if data.upazila_scope:
        query = query.where(Person.upazila == data.upazila_scope)
    if data.union_scope:
        query = query.where(Person.union_name == data.union_scope)

    result = await db.execute(query)
    total = result.scalar() or 0

    campaign = Campaign(
        **data.model_dump(),
        total_targets=total,
        status="pending",
    )
    db.add(campaign)
    await db.flush()
    await db.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/start", response_model=CampaignOut)
async def start_campaign(campaign_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign.status = "active"
    campaign.started_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(campaign)
    return campaign


@router.get("/{campaign_id}", response_model=CampaignOut)
async def get_campaign(campaign_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.get("/{campaign_id}/calls")
async def list_campaign_calls(campaign_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CallSession).where(CallSession.campaign_id == campaign_id).order_by(CallSession.created_at.desc())
    )
    return result.scalars().all()
