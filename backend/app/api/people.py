"""People management endpoints."""

from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional

from backend.app.database import get_db
from backend.app.models.person import Person
from backend.app.schemas.schemas import PersonOut, PersonFilter

router = APIRouter(prefix="/people", tags=["people"])


@router.get("", response_model=list[PersonOut])
async def list_people(
    district: Optional[str] = None,
    upazila: Optional[str] = None,
    union_name: Optional[str] = None,
    housing_type: Optional[str] = None,
    livelihood: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(Person)

    if district:
        query = query.where(Person.district == district)
    if upazila:
        query = query.where(Person.upazila == upazila)
    if union_name:
        query = query.where(Person.union_name == union_name)
    if housing_type:
        query = query.where(Person.housing_type_known == housing_type)
    if livelihood:
        query = query.where(Person.livelihood_known == livelihood)
    if search:
        query = query.where(
            or_(
                Person.name.ilike(f"%{search}%"),
                Person.village.ilike(f"%{search}%"),
                Person.phone.ilike(f"%{search}%"),
            )
        )

    query = query.order_by(Person.name).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/count")
async def count_people(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(func.count(Person.id)))
    return {"count": result.scalar() or 0}


@router.get("/districts")
async def list_districts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Person.district).where(Person.district.isnot(None)).distinct().order_by(Person.district)
    )
    return [r[0] for r in result.all()]


@router.get("/upazilas")
async def list_upazilas(district: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(Person.upazila).where(Person.upazila.isnot(None)).distinct().order_by(Person.upazila)
    if district:
        query = query.where(Person.district == district)
    result = await db.execute(query)
    return [r[0] for r in result.all()]


@router.get("/{person_id}", response_model=PersonOut)
async def get_person(person_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()
    if not person:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Person not found")
    return person
