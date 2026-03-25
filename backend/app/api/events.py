"""Hazard event management endpoints."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.database import get_db
from backend.app.models.hazard_event import HazardEvent
from backend.app.schemas.schemas import HazardEventCreate, HazardEventOut

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[HazardEventOut])
async def list_events(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HazardEvent).order_by(HazardEvent.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=HazardEventOut)
async def create_event(data: HazardEventCreate, db: AsyncSession = Depends(get_db)):
    event = HazardEvent(**data.model_dump())
    db.add(event)
    await db.flush()
    await db.refresh(event)
    return event


@router.get("/{event_id}", response_model=HazardEventOut)
async def get_event(event_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HazardEvent).where(HazardEvent.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
