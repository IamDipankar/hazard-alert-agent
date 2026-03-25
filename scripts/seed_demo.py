"""
Seed demo data for presentation — creates sample campaigns, events, call sessions,
extracted assessments, and map features.

Usage:
    python -m scripts.seed_demo
"""

import sys
import os
import uuid
import random
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from backend.app.database import Base
from backend.app.models.person import Person
from backend.app.models.hazard_event import HazardEvent
from backend.app.models.campaign import Campaign
from backend.app.models.call_session import CallSession, CallTurn
from backend.app.models.extracted_assessment import ExtractedAssessment
from backend.app.models.followup import Followup
from backend.app.models.map_feature import MapFeature


def main():
    from dotenv import load_dotenv
    load_dotenv()

    db_url = os.getenv("DATABASE_URL_SYNC", "postgresql://postgres:postgres@localhost:5432/hazard_alert")
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)

    random.seed(42)

    with Session(engine) as session:
        # Get existing people
        people = session.execute(select(Person)).scalars().all()
        if not people:
            print("⚠ No people found! Run import_people.py first.")
            return

        print(f"Found {len(people)} people in database")

        # ── Create hazard event ─────────────────────────────────────
        event = HazardEvent(
            id=uuid.uuid4(),
            event_type="cyclone",
            title="ঘূর্ণিঝড় রিমাল — সতর্কতা সংকেত ৭",
            severity="high",
            official_signal="সংকেত ৭",
            lead_time_hours=24,
            source="আবহাওয়া অধিদপ্তর",
            district_scope="Cox's Bazar,Chittagong,Noakhali,Patuakhali",
            description="ঘূর্ণিঝড় রিমাল বাংলাদেশের দক্ষিণ উপকূলে আঘাত হানতে পারে",
            is_active=True,
        )
        session.add(event)

        flood_event = HazardEvent(
            id=uuid.uuid4(),
            event_type="flood",
            title="বন্যা সতর্কতা — উত্তরাঞ্চল",
            severity="medium",
            lead_time_hours=48,
            source="বন্যা পূর্বাভাস ও সতর্কীকরণ কেন্দ্র",
            district_scope="Kurigram,Jamalpur,Sirajganj,Gaibandha",
            is_active=True,
        )
        session.add(flood_event)
        session.flush()

        # ── Create campaign ─────────────────────────────────────────
        campaign = Campaign(
            id=uuid.uuid4(),
            hazard_event_id=event.id,
            title="ঘূর্ণিঝড় রিমাল — জরুরি সতর্কতা কল",
            status="active",
            total_targets=len(people),
            started_at=datetime.now(timezone.utc) - timedelta(hours=2),
        )
        session.add(campaign)
        session.flush()

        # ── Create simulated call sessions ──────────────────────────
        housing_types = ["jhupri", "kacha", "semi-pucca", "pucca"]
        water_risks = ["tube_well_protected", "unprotected", "contaminated", "unknown"]
        latrine_risks = ["stable", "flood_prone", "damaged", "unknown"]
        livelihoods = ["fisherman", "fish_farmer", "farmer", "salt_farmer", "livestock_owner", "other"]
        conditions = ["no_impact", "water_rising", "strong_wind", "road_blocked", "embankment_issue"]
        assets = ["livestock", "nets", "boat", "seed", "crop", "documents"]
        vuln_types = ["elderly", "disability", "pregnancy", "children", "chronic_illness"]
        followup_types = ["human_callback", "volunteer_referral", "shelter_info", "medical_support", "none"]
        priorities = ["low", "medium", "high", "urgent"]

        completed = 0
        for i, person in enumerate(people[:min(len(people), 100)]):
            # Randomly assign call status
            status = random.choices(["completed", "completed", "completed", "partial", "failed"], weights=[5, 5, 5, 2, 1])[0]

            call = CallSession(
                id=uuid.uuid4(),
                campaign_id=campaign.id,
                person_id=person.id,
                hazard_event_id=event.id,
                mode="simulation",
                status=status,
                started_at=datetime.now(timezone.utc) - timedelta(minutes=random.randint(10, 120)),
                ended_at=datetime.now(timezone.utc) - timedelta(minutes=random.randint(1, 9)),
            )
            session.add(call)
            session.flush()

            if status in ("completed", "partial"):
                completed += 1
                housing = person.housing_type_known or random.choice(housing_types)
                livelihood = person.livelihood_known or random.choice(livelihoods)
                priority = random.choices(priorities, weights=[20, 35, 30, 15])[0]
                can_evac = random.choices(["yes", "no", "with_assistance"], weights=[5, 2, 3])[0]
                vuln = random.choice(["", random.choice(vuln_types), f"{random.choice(vuln_types)},{random.choice(vuln_types)}"])
                followup = random.choice(followup_types)
                awareness = random.choices(["yes", "no", "unsure"], weights=[6, 2, 2])[0]

                # Adjust priority based on characteristics
                if housing in ("jhupri", "kacha") and can_evac == "no":
                    priority = "urgent"
                elif vuln and housing in ("jhupri", "kacha"):
                    priority = "high"

                # Damage estimation
                damage_base = {"jhupri": 50000, "kacha": 100000, "semi-pucca": 200000, "pucca": 300000}
                severity_mult = {"low": 0.1, "medium": 0.3, "high": 0.6, "extreme": 0.9}
                est_damage = damage_base.get(housing, 100000) * severity_mult.get(event.severity, 0.3)
                est_damage *= random.uniform(0.7, 1.3)
                est_salvage = est_damage * random.uniform(0.1, 0.4)

                wash_urgency = random.choices(["none", "low", "medium", "high", "critical"], weights=[3, 3, 2, 1, 1])[0]
                med_urgency = random.choices(["none", "low", "medium", "high", "critical"], weights=[5, 3, 1, 0.5, 0.5])[0]

                assessment = ExtractedAssessment(
                    id=uuid.uuid4(),
                    call_session_id=call.id,
                    call_status=status,
                    warning_awareness=awareness,
                    district=person.district,
                    upazila=person.upazila,
                    union_name=person.union_name,
                    village=person.village,
                    gps_lat=person.lat,
                    gps_lng=person.lng,
                    housing_type=housing,
                    water_source_risk=random.choice(water_risks),
                    latrine_risk=random.choice(latrine_risks),
                    livelihood=livelihood,
                    vulnerable_members=vuln if vuln else None,
                    can_evacuate=can_evac,
                    current_local_condition=random.choice(conditions),
                    asset_at_risk=",".join(random.sample(assets, random.randint(0, 3))),
                    priority_class=priority,
                    recommended_followup=followup,
                    estimated_property_damage_risk_bdt=round(est_damage, 0),
                    estimated_property_salvageable_bdt=round(est_salvage, 0),
                    damage_confidence=round(random.uniform(0.2, 0.7), 2),
                    key_assets_named=",".join(random.sample(assets, random.randint(1, 3))),
                    evacuation_barrier_reason="রাস্তা বন্ধ" if can_evac == "no" else "",
                    medical_urgency=med_urgency,
                    wash_urgency=wash_urgency,
                    transcript_summary_bn=f"{person.name}-এর সাথে {event.event_type} সতর্কতা কল সম্পন্ন। অগ্রাধিকার: {priority}",
                    agent_notes_internal_en=f"Demo call for {person.name}. Priority: {priority}. Housing: {housing}",
                    support_priority_score={"low": 20, "medium": 40, "high": 65, "urgent": 85}.get(priority, 40) + random.uniform(-5, 5),
                )
                session.add(assessment)

                # Create followup if needed
                if followup != "none":
                    session.add(Followup(
                        id=uuid.uuid4(),
                        call_session_id=call.id,
                        followup_type=followup,
                        reason=f"Auto-generated from demo seed",
                        status="pending",
                    ))

                # Create map feature
                layer_flags = {
                    "vulnerable": bool(vuln),
                    "wash_risk": wash_urgency in ("high", "critical"),
                    "fragile_housing": housing in ("jhupri", "kacha"),
                    "evacuation_barrier": can_evac in ("no", "with_assistance"),
                    "livelihood_exposure": livelihood in ("fisherman", "fish_farmer", "salt_farmer"),
                    "urgent_callback": followup in ("human_callback", "medical_support"),
                    "property_damage": est_damage > 50000,
                    "salvage_opportunity": est_salvage > 10000,
                }

                session.add(MapFeature(
                    id=uuid.uuid4(),
                    person_id=person.id,
                    call_session_id=call.id,
                    lat=person.lat or 22.3 + random.uniform(-1, 1),
                    lng=person.lng or 89.5 + random.uniform(-1, 1),
                    priority_class=priority,
                    layer_flags_json=layer_flags,
                    popup_summary_bn=f"{person.name} — {housing} ঘর, {livelihood}, অগ্রাধিকার: {priority}",
                    person_name=person.name,
                    district=person.district,
                    upazila=person.upazila,
                    union_name=person.union_name,
                    village=person.village,
                    housing_type=housing,
                    livelihood=livelihood,
                    can_evacuate=can_evac,
                    vulnerable_members=vuln if vuln else None,
                    recommended_followup=followup,
                    estimated_damage_bdt=round(est_damage, 0),
                    estimated_salvageable_bdt=round(est_salvage, 0),
                ))

        campaign.completed_calls = completed
        campaign.failed_calls = len(people[:min(len(people), 100)]) - completed
        session.commit()

    print(f"\n✅ Demo seed complete:")
    print(f"   Events: 2")
    print(f"   Campaigns: 1")
    print(f"   Calls: {min(len(people), 100)}")
    print(f"   Completed: {completed}")
    print(f"   Assessments + map features created")


if __name__ == "__main__":
    main()
