"""Map endpoints — GeoJSON features for the vulnerability map."""

import json
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.database import get_db
from backend.app.models.map_feature import MapFeature

router = APIRouter(prefix="/map", tags=["map"])


@router.get("/geojson")
async def get_geojson(
    district: Optional[str] = None,
    upazila: Optional[str] = None,
    union_name: Optional[str] = None,
    village: Optional[str] = None,
    housing_type: Optional[str] = None,
    livelihood: Optional[str] = None,
    priority_class: Optional[str] = None,
    followup_type: Optional[str] = None,
    layer: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Return GeoJSON FeatureCollection of map features with filtering."""
    query = select(MapFeature)

    if district:
        query = query.where(MapFeature.district == district)
    if upazila:
        query = query.where(MapFeature.upazila == upazila)
    if union_name:
        query = query.where(MapFeature.union_name == union_name)
    if village:
        query = query.where(MapFeature.village == village)
    if housing_type:
        query = query.where(MapFeature.housing_type == housing_type)
    if livelihood:
        query = query.where(MapFeature.livelihood == livelihood)
    if priority_class:
        query = query.where(MapFeature.priority_class == priority_class)
    if followup_type:
        query = query.where(MapFeature.recommended_followup == followup_type)

    # Layer-specific filtering based on layer_flags_json
    if layer:
        query = query.where(MapFeature.layer_flags_json[layer].as_boolean() == True)

    result = await db.execute(query)
    features = result.scalars().all()

    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [f.lng, f.lat],
                },
                "properties": {
                    "id": str(f.id),
                    "person_name": f.person_name,
                    "district": f.district,
                    "upazila": f.upazila,
                    "union_name": f.union_name,
                    "village": f.village,
                    "housing_type": f.housing_type,
                    "livelihood": f.livelihood,
                    "can_evacuate": f.can_evacuate,
                    "vulnerable_members": f.vulnerable_members,
                    "priority_class": f.priority_class or "low",
                    "recommended_followup": f.recommended_followup,
                    "estimated_damage_bdt": f.estimated_damage_bdt,
                    "estimated_salvageable_bdt": f.estimated_salvageable_bdt,
                    "popup_summary_bn": f.popup_summary_bn,
                    "layer_flags": f.layer_flags_json or {},
                },
            }
            for f in features
        ],
    }

    return JSONResponse(content=geojson)


@router.get("/export/csv")
async def export_csv(
    district: Optional[str] = None,
    upazila: Optional[str] = None,
    priority_class: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Export map features as CSV."""
    from fastapi.responses import StreamingResponse
    import csv
    import io

    query = select(MapFeature)
    if district:
        query = query.where(MapFeature.district == district)
    if upazila:
        query = query.where(MapFeature.upazila == upazila)
    if priority_class:
        query = query.where(MapFeature.priority_class == priority_class)

    result = await db.execute(query)
    features = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "name", "district", "upazila", "union", "village", "lat", "lng",
        "housing_type", "livelihood", "priority_class", "can_evacuate",
        "vulnerable_members", "followup", "estimated_damage_bdt", "salvageable_bdt",
    ])
    for f in features:
        writer.writerow([
            f.person_name, f.district, f.upazila, f.union_name, f.village,
            f.lat, f.lng, f.housing_type, f.livelihood, f.priority_class,
            f.can_evacuate, f.vulnerable_members, f.recommended_followup,
            f.estimated_damage_bdt, f.estimated_salvageable_bdt,
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=map_export.csv"},
    )
