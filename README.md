# 🌊 Hazard Alert Agent — দুর্যোগ সতর্কতা

A production-style hackathon prototype of a Bengali-only disaster early-warning voice AI system for Bangladesh — focused on cyclone, storm surge, flood, flash flood, waterlogging, landslide, and river erosion risk.

## 🎯 What it does

1. **Operator Dashboard** — create alert campaigns, select target people, monitor call progress
2. **Call Simulation** — full Bengali voice conversation in-browser (TTS + ASR + LLM)
3. **RAG-Powered Guidance** — retrieves context-aware safety instructions from uploaded playbooks
4. **Structured Extraction** — extracts housing, vulnerability, WASH risk, livelihood, and damage data
5. **Vulnerability Map** — interactive Leaflet map with priority-colored markers and 8 thematic layers
6. **Analytics Dashboard** — awareness rates, priority distributions, damage estimates, and more

## 🛠 Tech Stack

| Layer | Tech |
|-------|------|
| Backend | FastAPI, SQLAlchemy, PostgreSQL, pgvector, Alembic |
| Frontend | React, TypeScript, Vite, Tailwind CSS, Leaflet, Recharts |
| AI/Voice | OpenAI GPT-4o-mini, Google Cloud TTS, ai4bharat ASR |
| Deploy | Docker Compose, Koyeb-ready |

## 🚀 Quick Start (Local)

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env with your OPENAI_API_KEY (required for LLM features)

# 2. Start all services
docker-compose up --build

# 3. Import people from spreadsheet
docker-compose exec backend python -m scripts.import_people

# 4. Ingest RAG documents
docker-compose exec backend python -m scripts.ingest_rag_docs

# 5. Seed demo data
docker-compose exec backend python -m scripts.seed_demo
```

Open:
- **Frontend**: http://localhost:5173
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI route modules
│   │   ├── models/       # SQLAlchemy models (11 tables)
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # AI/voice/RAG/extraction services
│   │   ├── config.py     # Pydantic Settings
│   │   ├── database.py   # Async SQLAlchemy engine
│   │   └── main.py       # FastAPI app entry point
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/        # Dashboard, People, Campaigns, CallSim, Map, Analytics
│   │   ├── components/   # Layout, shared components
│   │   ├── api.ts        # API client
│   │   ├── App.tsx        # Routing
│   │   └── index.css     # Design system
│   ├── Dockerfile
│   └── package.json
├── scripts/
│   ├── import_people.py  # XLSX → PostgreSQL
│   ├── ingest_rag_docs.py # DOCX → pgvector chunks
│   ├── seed_demo.py      # Demo data generator
│   └── run_local_gpu_asr.py # Standalone ASR worker
├── alembic/              # Database migrations
├── docs/                 # Architecture, data model, deployment
├── docker-compose.yml
├── .env.example
└── instruction.md        # AI agent system instruction
```

## 🗺️ Key URLs

| Route | Description |
|-------|-------------|
| `/` | Dashboard |
| `/people` | People list with filters |
| `/campaigns` | Campaign management |
| `/call/:personId` | Call simulation |
| `/simulate-call?person_id=X&event_id=Y` | Direct call simulation |
| `/map` | Vulnerability map |
| `/analytics` | Analytics dashboard |

## 📊 Database Schema

13 tables: `people`, `hazard_events`, `campaigns`, `call_sessions`, `call_turns`, `extracted_assessments`, `followups`, `map_features`, `rag_documents`, `rag_chunks`, `audit_logs`

## 🔑 Environment Variables

See `.env.example` for the full list. Key ones:
- `OPENAI_API_KEY` — required for LLM conversation and extraction
- `GOOGLE_APPLICATION_CREDENTIALS` — optional, for Google TTS
- `DATABASE_URL` — PostgreSQL connection string
- `MAPBOX_TOKEN` — optional, for Mapbox tiles

## 🌐 Deployment (Koyeb)

See `docs/deployment_koyeb.md` for step-by-step instructions.

## 📋 Demo Flow

1. Open Dashboard → see KPIs
2. Go to People → browse imported persons
3. Click "কল করুন" on any person → starts call simulation
4. Bengali AI greeting plays → respond via text input
5. AI asks questions, gives guidance, extracts data
6. End call → see extracted assessment
7. Go to Map → see priority-colored markers with Bengali popups
8. Go to Analytics → see charts and distributions

## 📝 License

Built for hackathon purposes. All safety guidelines sourced from RIMES Bangladesh.
