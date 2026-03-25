"""
Conversation orchestrator — drives the Bengali conversation using OpenAI.
Implements a state machine with hazard-specific guidance and personalization.
"""

import logging
import json
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.rag_retriever import retrieve_guidance
from backend.app.config import settings

logger = logging.getLogger(__name__)

# Conversation stages in order
STAGES = [
    "greeting",           # 1. Greeting and consent
    "awareness",          # 2. Warning awareness check
    "situation",          # 3. Situation framing
    "hazard_guidance",    # 4. Hazard-specific guidance
    "household",          # 5. Household profiling questions
    "vulnerability",      # 6. Vulnerability assessment
    "local_condition",    # 7. Current local condition check
    "wash_risk",          # 8. WASH risk check
    "evacuation",         # 9. Evacuation ability check
    "asset_risk",         # 10. Asset/livelihood risk check
    "personalized",       # 11. Personalized guidance
    "confirmation",       # 12. Extraction confirmation
    "closing",            # 13. Closing
    "closed",             # Final state
]


def _next_stage(current: str) -> str:
    """Get the next conversation stage."""
    try:
        idx = STAGES.index(current)
        if idx < len(STAGES) - 1:
            return STAGES[idx + 1]
    except ValueError:
        pass
    return "closed"


def _build_system_prompt(person, event, rag_context: list[dict], current_stage: str) -> str:
    """Build the system prompt with person profile, event context, and RAG guidance."""

    # Person context
    person_info = ""
    if person:
        person_info = f"""
ব্যক্তির তথ্য (Person Profile):
- নাম: {person.name or 'অজানা'}
- জেলা: {person.district or 'অজানা'}
- উপজেলা: {person.upazila or 'অজানা'}
- ইউনিয়ন: {person.union_name or 'অজানা'}
- গ্রাম: {person.village or 'অজানা'}
- ঘরের ধরন: {person.housing_type_known or 'অজানা'}
- জীবিকা: {person.livelihood_known or 'অজানা'}
- ঝুঁকিপূর্ণ সদস্য: {person.vulnerable_members_known or 'অজানা'}
- পানির উৎস: {person.water_source_known or 'অজানা'}
- ল্যাট্রিন: {person.latrine_type_known or 'অজানা'}
"""

    # Event context
    event_info = ""
    if event:
        event_info = f"""
দুর্যোগের তথ্য (Hazard Event):
- ধরন: {event.event_type}
- শিরোনাম: {event.title}
- তীব্রতা: {event.severity}
- সরকারি সংকেত: {event.official_signal or 'N/A'}
- হাতে সময়: {event.lead_time_hours or 'অজানা'} ঘণ্টা
- উৎস: {event.source or 'আবহাওয়া অধিদপ্তর'}
"""

    # RAG guidance
    rag_text = ""
    if rag_context:
        chunks = []
        for ctx in rag_context[:5]:
            chunks.append(f"[{ctx.get('heading', '')}]: {ctx.get('content', '')}")
        rag_text = "\n\nপ্রাসঙ্গিক নির্দেশনা (Retrieved Guidance):\n" + "\n".join(chunks)

    system_prompt = f"""You are a Bengali-speaking disaster safety voice assistant for vulnerable communities in Bangladesh.

STRICT RULES:
1. ALWAYS respond in Bengali only. Never use English in your response.
2. Be calm, respectful, concise, and practical.
3. Never contradict official warning/evacuation instructions.
4. Never fabricate shelter locations or promise rescue/compensation.
5. If the person is in immediate danger, stop asking questions and prioritize life safety.
6. Give 3-5 key actions at a time, never more.
7. Life safety > evacuation > medicine > safe water > documents > assets.

CURRENT CONVERSATION STAGE: {current_stage}
Stage sequence: greeting → awareness → situation → hazard_guidance → household → vulnerability → local_condition → wash_risk → evacuation → asset_risk → personalized → confirmation → closing

STAGE INSTRUCTIONS:
- greeting: Introduce yourself as দুর্যোগ সুরক্ষা সহায়তা সেবা. Mention the warning. Ask if they can talk now. Be brief.
- awareness: Ask if they know about the warning/alert.
- situation: Brief hazard description in Bengali.
- hazard_guidance: Give 3-5 immediate safety actions based on the hazard type.
- household: Ask about house type (ঝুপড়ি/কাঁচা/আধাপাকা/পাকা) and family members.
- vulnerability: Ask about elderly, disabled, pregnant women, children, or chronically ill.
- local_condition: Ask about current conditions (water level, wind, road status).
- wash_risk: Ask about drinking water source and latrine condition.
- evacuation: Ask if they can move to a safe place. If not, ask why.
- asset_risk: Ask about livestock, fishing nets, boats, seeds, crops at risk.
- personalized: Give personalized advice based on all gathered info.
- confirmation: Briefly summarize key risks and verify. Ask if they need anything else.
- closing: Thank them. Remind: keep phone on, share warning with neighbors, follow official instructions.

WHEN TO SWITCH TO NEXT STAGE:
- After the person responds to your question for the current stage, move to the next stage.
- Include your response AND the next question in the same message.
- If danger is imminent (from their response), skip to life safety guidance immediately.

YOUR RESPONSE FORMAT:
Respond with a JSON object:
{{"response_bn": "your Bengali response text here", "next_stage": "the next stage name", "urgency": "normal|elevated|urgent|critical"}}

{person_info}
{event_info}
{rag_text}
"""
    return system_prompt


async def orchestrate_turn(
    session_id: str,
    person,
    event,
    user_message: Optional[str],
    conversation_history: list[dict],
    current_stage: str,
    db: AsyncSession,
) -> tuple[str, str, str]:
    """
    Orchestrate one conversation turn.
    Returns: (response_bn, next_stage, urgency)
    """

    # Retrieve RAG context
    hazard_type = event.event_type if event else None
    query_for_rag = user_message or f"greeting {hazard_type or 'disaster'}"

    rag_context = await retrieve_guidance(
        db=db,
        query_text=query_for_rag,
        hazard_type=hazard_type,
        phase="before",
    )

    system_prompt = _build_system_prompt(person, event, rag_context, current_stage)

    # Build messages for OpenAI
    messages = [{"role": "system", "content": system_prompt}]

    for turn in conversation_history:
        role = "assistant" if turn["role"] == "agent" else "user"
        messages.append({"role": role, "content": turn["content"]})

    if user_message:
        messages.append({"role": "user", "content": user_message})
    else:
        # Initial greeting — no user message yet
        messages.append({"role": "user", "content": "[কল শুরু হলো — প্রথম অভিবাদন দিন]"})

    # Call OpenAI
    try:
        if settings.OPENAI_API_KEY:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            parsed = json.loads(content)

            response_bn = parsed.get("response_bn", "")
            next_stage = parsed.get("next_stage", _next_stage(current_stage))
            urgency = parsed.get("urgency", "normal")

            return response_bn, next_stage, urgency

    except Exception as e:
        logger.error(f"OpenAI call failed: {e}")

    # Fallback responses when OpenAI is not available
    return _fallback_response(current_stage, person, event)


def _fallback_response(stage: str, person, event) -> tuple[str, str, str]:
    """Generate fallback Bengali responses when OpenAI is not configured."""

    name = person.name if person else "ভাই/আপা"
    hazard = event.event_type if event else "দুর্যোগ"

    hazard_bn = {
        "cyclone": "ঘূর্ণিঝড়",
        "storm_surge": "জলোচ্ছ্বাস",
        "flood": "বন্যা",
        "flash_flood": "আকস্মিক বন্যা",
        "heavy_rainfall": "ভারী বৃষ্টিপাত",
        "waterlogging": "জলাবদ্ধতা",
        "landslide": "ভূমিধস",
        "river_erosion": "নদী ভাঙন",
    }.get(hazard, "দুর্যোগ")

    responses = {
        "greeting": (
            f"আসসালামু আলাইকুম, {name}। আমি দুর্যোগ সুরক্ষা সহায়তা সেবা থেকে কথা বলছি। "
            f"আপনার এলাকায় {hazard_bn}-এর সতর্কতা জারি হয়েছে। আপনি কি এখন একটু কথা বলতে পারবেন?",
            "awareness",
            "normal",
        ),
        "awareness": (
            f"আপনি কি {hazard_bn}-এর সতর্কতার কথা আগে থেকে জানতেন?",
            "situation",
            "normal",
        ),
        "situation": (
            f"আপনার এলাকায় আগামী কয়েক ঘণ্টায় {hazard_bn}-এর প্রভাব পড়তে পারে। "
            "এখনই কিছু গুরুত্বপূর্ণ পদক্ষেপ নেওয়া দরকার।",
            "hazard_guidance",
            "normal",
        ),
        "hazard_guidance": (
            "জরুরি পদক্ষেপ:\n"
            "১. নিরাপদ আশ্রয়ে যান\n"
            "২. খাবার পানি সংরক্ষণ করুন\n"
            "৩. গুরুত্বপূর্ণ কাগজপত্র ও ওষুধ সাথে রাখুন\n"
            "৪. প্রতিবেশীদের সতর্ক করুন\n\n"
            "আপনার ঘর কি ধরনের? ঝুপড়ি, কাঁচা, আধাপাকা, নাকি পাকা?",
            "household",
            "normal",
        ),
        "household": (
            "আপনার পরিবারে কি বয়স্ক, প্রতিবন্ধী, গর্ভবতী মহিলা, ছোট শিশু, বা দীর্ঘমেয়াদী অসুস্থ কেউ আছেন?",
            "vulnerability",
            "normal",
        ),
        "vulnerability": (
            "আপনার এলাকায় এখন কি অবস্থা? পানি কি বাড়ছে? বাতাস কেমন? রাস্তা কি চলাচলের যোগ্য?",
            "local_condition",
            "normal",
        ),
        "local_condition": (
            "আপনি কোথা থেকে খাবার পানি পান? টিউবওয়েল কি নিরাপদ আছে? আপনার ল্যাট্রিন কি বন্যার ঝুঁকিতে আছে?",
            "wash_risk",
            "normal",
        ),
        "wash_risk": (
            "আপনি কি নিরাপদ স্থানে যেতে পারবেন? কোনো বাধা আছে কি?",
            "evacuation",
            "normal",
        ),
        "evacuation": (
            "আপনার কি গবাদিপশু, মাছের জাল, নৌকা, বীজ, বা ফসল ঝুঁকিতে আছে?",
            "asset_risk",
            "normal",
        ),
        "asset_risk": (
            f"{name}, আপনার তথ্যের ভিত্তিতে আমার পরামর্শ:\n"
            "১. এখনই পরিবারকে নিরাপদ স্থানে নিন\n"
            "২. বিশুদ্ধ পানি মজুদ রাখুন\n"
            "৩. সম্ভব হলে গবাদিপশু উঁচু স্থানে সরান\n"
            "আর কিছু জানতে চান?",
            "confirmation",
            "normal",
        ),
        "confirmation": (
            "ধন্যবাদ। আপনার জন্য আমাদের শুভকামনা। ফোন চালু রাখুন, সরকারি নির্দেশনা মানুন, "
            "আর প্রতিবেশীদেরও সতর্ক করুন। আল্লাহ হাফেজ।",
            "closed",
            "normal",
        ),
        "closing": (
            "ধন্যবাদ। সবাই নিরাপদ থাকুন। আল্লাহ হাফেজ।",
            "closed",
            "normal",
        ),
    }

    return responses.get(stage, responses["greeting"])
