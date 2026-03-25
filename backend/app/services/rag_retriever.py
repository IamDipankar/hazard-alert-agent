"""
RAG retriever — retrieves relevant safety guidance chunks from pgvector.
Falls back to a set of hardcoded guidance if pgvector isn't available.
"""

import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from backend.app.models.rag import RAGChunk

logger = logging.getLogger(__name__)


async def retrieve_guidance(
    db: AsyncSession,
    query_text: str,
    hazard_type: Optional[str] = None,
    phase: Optional[str] = None,
    housing_type: Optional[str] = None,
    livelihood: Optional[str] = None,
    vulnerability_group: Optional[str] = None,
    top_k: int = 5,
) -> list[dict]:
    """
    Retrieve relevant guidance chunks from the RAG store.
    Uses pgvector similarity search with optional metadata filters.
    """
    try:
        # Try to get embedding for the query
        embedding = await _get_embedding(query_text)

        if embedding is None:
            # No OpenAI key — return metadata-filtered results without vector search
            return await _metadata_search(db, hazard_type, phase, housing_type, livelihood, top_k)

        # Build filtered vector search
        query = select(
            RAGChunk.content,
            RAGChunk.heading,
            RAGChunk.hazard_type,
            RAGChunk.phase,
            RAGChunk.action_priority,
            RAGChunk.metadata_json,
        )

        if hazard_type:
            query = query.where(
                (RAGChunk.hazard_type == hazard_type) | (RAGChunk.hazard_type.is_(None))
            )
        if phase:
            query = query.where(
                (RAGChunk.phase == phase) | (RAGChunk.phase.is_(None))
            )
        if housing_type:
            query = query.where(
                (RAGChunk.housing_type == housing_type) | (RAGChunk.housing_type.is_(None))
            )
        if livelihood:
            query = query.where(
                (RAGChunk.livelihood == livelihood) | (RAGChunk.livelihood.is_(None))
            )

        # Order by vector similarity
        query = query.order_by(RAGChunk.embedding.cosine_distance(embedding)).limit(top_k)

        result = await db.execute(query)
        rows = result.all()

        return [
            {
                "content": row[0],
                "heading": row[1],
                "hazard_type": row[2],
                "phase": row[3],
                "action_priority": row[4],
            }
            for row in rows
        ]

    except Exception as e:
        logger.warning(f"RAG retrieval error: {e}")
        return _fallback_guidance(hazard_type)


async def _metadata_search(
    db: AsyncSession,
    hazard_type: Optional[str],
    phase: Optional[str],
    housing_type: Optional[str],
    livelihood: Optional[str],
    top_k: int,
) -> list[dict]:
    """Fallback: search by metadata only without vector similarity."""
    query = select(RAGChunk.content, RAGChunk.heading, RAGChunk.hazard_type, RAGChunk.phase, RAGChunk.action_priority)

    if hazard_type:
        query = query.where(RAGChunk.hazard_type == hazard_type)
    if phase:
        query = query.where(RAGChunk.phase == phase)

    query = query.limit(top_k)
    result = await db.execute(query)
    rows = result.all()

    if not rows:
        return _fallback_guidance(hazard_type)

    return [
        {
            "content": row[0],
            "heading": row[1],
            "hazard_type": row[2],
            "phase": row[3],
            "action_priority": row[4],
        }
        for row in rows
    ]


async def _get_embedding(text: str) -> Optional[list[float]]:
    """Get embedding from OpenAI."""
    try:
        from openai import AsyncOpenAI
        from backend.app.config import settings

        if not settings.OPENAI_API_KEY:
            return None

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding
    except Exception as e:
        logger.warning(f"Embedding generation failed: {e}")
        return None


def _fallback_guidance(hazard_type: Optional[str] = None) -> list[dict]:
    """Hardcoded fallback guidance when RAG is not available."""

    guidance = {
        "cyclone": [
            {
                "content": "ঘূর্ণিঝড়ের সময় পাকা আশ্রয়কেন্দ্রে যান। জানালা-দরজা বন্ধ রাখুন। বৈদ্যুতিক লাইন থেকে দূরে থাকুন। খাবার পানি ও শুকনো খাবার সংরক্ষণ করুন।",
                "heading": "ঘূর্ণিঝড় সুরক্ষা",
                "hazard_type": "cyclone",
                "phase": "before",
                "action_priority": "life_safety",
            },
        ],
        "flood": [
            {
                "content": "বন্যার সময় উঁচু স্থানে আশ্রয় নিন। বিশুদ্ধ পানি সংরক্ষণ করুন। বিদ্যুৎ সংযোগ বিচ্ছিন্ন করুন। গবাদিপশু নিরাপদ স্থানে সরান।",
                "heading": "বন্যা সুরক্ষা",
                "hazard_type": "flood",
                "phase": "before",
                "action_priority": "life_safety",
            },
        ],
    }

    default = [
        {
            "content": "দুর্যোগের সময় নিরাপদ আশ্রয়ে যান। গুরুত্বপূর্ণ কাগজপত্র ও ওষুধ সাথে নিন। প্রতিবেশীদের সতর্ক করুন।",
            "heading": "সাধারণ সুরক্ষা",
            "hazard_type": "general",
            "phase": "before",
            "action_priority": "life_safety",
        },
    ]

    return guidance.get(hazard_type, default) if hazard_type else default
