# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│  Dashboard │ People │ Campaigns │ Call Sim │ Map │ Analytics │
│            Vite + TypeScript + Tailwind + Leaflet        │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP / REST
┌────────────────────────┼────────────────────────────────┐
│                  Backend (FastAPI)                       │
│  ┌──────────┐  ┌───────────┐  ┌──────────────────┐     │
│  │ API Routes│  │ Services  │  │ Background Jobs  │     │
│  │ /people  │  │ ASR       │  │ (future Celery)  │     │
│  │ /events  │  │ TTS       │  └──────────────────┘     │
│  │ /campaigns│ │ RAG       │                            │
│  │ /calls   │  │ LLM Orch. │  ┌──────────────────┐     │
│  │ /analytics│ │ Extractor │  │ Alembic Migrations│    │
│  │ /map     │  │ Estimator │  └──────────────────┘     │
│  └──────────┘  └───────────┘                            │
└──────────┬────────────────┬────────────────────────────┘
           │                │
  ┌────────┴───────┐  ┌────┴──────────┐
  │ PostgreSQL     │  │ Redis         │
  │ + pgvector     │  │ (queue/cache) │
  │ 11 tables      │  └───────────────┘
  └────────────────┘

External Services:
  - OpenAI API (GPT-4o-mini for conversation + extraction)
  - Google Cloud TTS (Bengali voice synthesis)
  - ai4bharat ASR (GPU worker for Bengali speech recognition)
```

## Component Responsibilities

### API Layer
- RESTful endpoints for all CRUD operations
- WebSocket support for real-time call simulation (future)
- Request validation via Pydantic schemas

### Service Layer
- **conversation_orchestrator.py** — 13-stage Bengali conversation state machine
- **rag_retriever.py** — pgvector similarity search with metadata filtering
- **risk_extractor.py** — structured data extraction from transcripts
- **asr_service.py** — Bengali speech recognition (GPU or mock)
- **tts_service.py** — Bengali text-to-speech (Google Cloud or mock)

### Data Flow

```
Person DB + Hazard Event
        ↓
  Call Session Created
        ↓
  Greeting Generated (LLM + RAG)
        ↓
  User Responds (Text or ASR)
        ↓
  LLM Orchestrates Response (Bengali)
        ↓
  TTS Synthesizes Audio
        ↓
  Repeat per conversation stage
        ↓
  Call Ends → Extract Assessment
        ↓
  Create MapFeature + Followup
        ↓
  Dashboard + Map Updated
```
