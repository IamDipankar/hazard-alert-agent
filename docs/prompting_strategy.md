# Prompting Strategy

## Conversation Orchestrator

The AI agent uses a **13-stage state machine** for conversation flow:

1. **Greeting** — introduce as দুর্যোগ সুরক্ষা সহায়তা সেবা, mention warning, ask consent
2. **Awareness** — check if they know about the warning
3. **Situation** — brief hazard description
4. **Hazard Guidance** — 3-5 immediate safety actions
5. **Household** — house type question
6. **Vulnerability** — elderly, disabled, pregnant, children
7. **Local Condition** — water level, wind, road status
8. **WASH Risk** — water source and latrine condition
9. **Evacuation** — ability to move, barriers
10. **Asset Risk** — livestock, nets, boat, seeds, crops
11. **Personalized** — tailored advice based on all gathered info
12. **Confirmation** — summarize and verify
13. **Closing** — thank, remind to keep phone on, share with neighbors

## System Prompt Design

Each turn builds a system prompt with:
- Fixed safety rules (Bengali-only, no false reassurance, life safety priority)
- Current conversation stage and instructions
- Person profile (from database)
- Hazard event context (type, severity, lead time)
- Retrieved RAG guidance chunks (from pgvector)

## Extraction Schema

Uses OpenAI structured output (JSON mode) to extract 25+ fields from the transcript.

## Safety Guards
- Never contradict official instructions
- Never fabricate shelter locations
- Stop questions in active danger → prioritize guidance
- Escalation triggers for urgent situations

## RAG Strategy
- Chunks embedded with OpenAI text-embedding-3-small
- Retrieved by vector similarity + metadata filters (hazard type, phase, housing, livelihood)
- Grounding: prevents hallucination by providing real guidance text
