"""Call session + conversation endpoints — the core of the voice simulation."""

import uuid
import base64
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.database import get_db
from backend.app.models.call_session import CallSession, CallTurn
from backend.app.models.person import Person
from backend.app.models.hazard_event import HazardEvent
from backend.app.schemas.schemas import CallSessionCreate, CallSessionOut, ChatMessage, ChatResponse
from backend.app.services.conversation_orchestrator import orchestrate_turn
from backend.app.services.tts_service import synthesize_bengali
from backend.app.services.asr_service import transcribe_audio
from backend.app.services.risk_extractor import extract_from_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/calls", tags=["calls"])


@router.post("", response_model=CallSessionOut)
async def create_call(data: CallSessionCreate, db: AsyncSession = Depends(get_db)):
    """Create a new call session for a person."""
    # Verify person exists
    person_result = await db.execute(select(Person).where(Person.id == data.person_id))
    person = person_result.scalar_one_or_none()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    session = CallSession(
        person_id=data.person_id,
        hazard_event_id=data.hazard_event_id,
        campaign_id=data.campaign_id,
        mode="simulation",
        status="pending",
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)
    return session


@router.post("/{call_id}/start", response_model=ChatResponse)
async def start_call(call_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Start a call — generates the initial Bengali greeting."""
    result = await db.execute(select(CallSession).where(CallSession.id == call_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Call session not found")

    # Get person profile
    person_result = await db.execute(select(Person).where(Person.id == session.person_id))
    person = person_result.scalar_one_or_none()

    # Get hazard event if available
    event = None
    if session.hazard_event_id:
        event_result = await db.execute(select(HazardEvent).where(HazardEvent.id == session.hazard_event_id))
        event = event_result.scalar_one_or_none()

    session.status = "active"
    session.started_at = datetime.now(timezone.utc)

    # Generate initial greeting
    greeting_text, stage, urgency = await orchestrate_turn(
        session_id=str(session.id),
        person=person,
        event=event,
        user_message=None,  # No user message yet — this is the greeting
        conversation_history=[],
        current_stage="greeting",
        db=db,
    )

    session.conversation_stage = stage

    # Save the greeting turn
    turn = CallTurn(
        call_session_id=session.id,
        turn_number=1,
        role="agent",
        content_bn=greeting_text,
    )
    db.add(turn)
    await db.flush()

    # TTS
    audio_url = await synthesize_bengali(greeting_text)

    return ChatResponse(
        text_bn=greeting_text,
        audio_url=audio_url,
        stage=stage,
        urgency=urgency,
    )


@router.post("/{call_id}/chat", response_model=ChatResponse)
async def chat_turn(call_id: uuid.UUID, msg: ChatMessage, db: AsyncSession = Depends(get_db)):
    """Process a user's message (text or audio) and return the AI response."""
    result = await db.execute(select(CallSession).where(CallSession.id == call_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Call session not found")

    # Get person and event
    person_result = await db.execute(select(Person).where(Person.id == session.person_id))
    person = person_result.scalar_one_or_none()

    event = None
    if session.hazard_event_id:
        event_result = await db.execute(select(HazardEvent).where(HazardEvent.id == session.hazard_event_id))
        event = event_result.scalar_one_or_none()

    # Transcribe audio if provided
    user_text = msg.text
    if msg.audio_base64 and not user_text:
        audio_bytes = base64.b64decode(msg.audio_base64)
        user_text = await transcribe_audio(audio_bytes)

    if not user_text:
        raise HTTPException(status_code=400, detail="No text or audio provided")

    # Get conversation history
    turns_result = await db.execute(
        select(CallTurn)
        .where(CallTurn.call_session_id == call_id)
        .order_by(CallTurn.turn_number)
    )
    turns = turns_result.scalars().all()
    history = [{"role": t.role, "content": t.content_bn or ""} for t in turns]

    # Save user turn
    user_turn_number = len(turns) + 1
    user_turn = CallTurn(
        call_session_id=session.id,
        turn_number=user_turn_number,
        role="user",
        content_bn=user_text,
    )
    db.add(user_turn)

    # Orchestrate AI response
    response_text, stage, urgency = await orchestrate_turn(
        session_id=str(session.id),
        person=person,
        event=event,
        user_message=user_text,
        conversation_history=history,
        current_stage=session.conversation_stage,
        db=db,
    )

    session.conversation_stage = stage
    session.urgency_level = urgency

    # Save agent turn
    agent_turn = CallTurn(
        call_session_id=session.id,
        turn_number=user_turn_number + 1,
        role="agent",
        content_bn=response_text,
    )
    db.add(agent_turn)
    await db.flush()

    # Check if conversation is ending
    is_final = stage == "closed"

    # TTS
    audio_url = await synthesize_bengali(response_text)

    return ChatResponse(
        text_bn=response_text,
        audio_url=audio_url,
        stage=stage,
        urgency=urgency,
        is_final=is_final,
    )


@router.post("/{call_id}/end")
async def end_call(call_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """End a call and trigger extraction."""
    result = await db.execute(select(CallSession).where(CallSession.id == call_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Call session not found")

    session.status = "completed"
    session.ended_at = datetime.now(timezone.utc)

    # Build full transcript
    turns_result = await db.execute(
        select(CallTurn)
        .where(CallTurn.call_session_id == call_id)
        .order_by(CallTurn.turn_number)
    )
    turns = turns_result.scalars().all()
    transcript_lines = []
    for t in turns:
        role_label = "এজেন্ট" if t.role == "agent" else "ব্যক্তি"
        transcript_lines.append(f"{role_label}: {t.content_bn or ''}")
    session.transcript_text = "\n".join(transcript_lines)

    # Get person and event for extraction context
    person_result = await db.execute(select(Person).where(Person.id == session.person_id))
    person = person_result.scalar_one_or_none()

    event = None
    if session.hazard_event_id:
        event_result = await db.execute(select(HazardEvent).where(HazardEvent.id == session.hazard_event_id))
        event = event_result.scalar_one_or_none()

    # Run extraction
    try:
        assessment = await extract_from_session(session, person, event, db)
        session.extraction_json = assessment.raw_extraction if assessment else None
    except Exception as e:
        logger.error(f"Extraction failed for call {call_id}: {e}")

    await db.flush()

    return {"status": "completed", "call_id": str(call_id)}


@router.get("/{call_id}", response_model=CallSessionOut)
async def get_call(call_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CallSession).where(CallSession.id == call_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Call session not found")
    return session


@router.get("/{call_id}/turns")
async def get_call_turns(call_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CallTurn)
        .where(CallTurn.call_session_id == call_id)
        .order_by(CallTurn.turn_number)
    )
    turns = result.scalars().all()
    return [
        {
            "turn_number": t.turn_number,
            "role": t.role,
            "content_bn": t.content_bn,
            "audio_url": t.audio_url,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in turns
    ]
