# Koyeb Deployment Guide

## Architecture on Koyeb

| Service | Koyeb Type | Notes |
|---------|-----------|-------|
| Backend API | Web Service | Python, port 8000 |
| Frontend | Web Service | Node.js, port 5173 (or static build) |
| PostgreSQL | Koyeb Managed DB | With pgvector extension |
| Redis | External (Upstash) | Or Koyeb addon if available |
| ASR Worker | GPU Web Service | RTX-4000-SFF-ADA recommended |

## Step-by-step

### 1. Create PostgreSQL Database
- Create a Koyeb managed PostgreSQL database
- Enable pgvector extension: `CREATE EXTENSION vector;`
- Note the connection string

### 2. Deploy Backend
```bash
# In Koyeb dashboard:
# - Source: GitHub repo → backend/
# - Build: Dockerfile at backend/Dockerfile
# - Port: 8000
# - Environment variables: (set all from .env.example)
#   DATABASE_URL=postgresql+asyncpg://...
#   DATABASE_URL_SYNC=postgresql://...
#   OPENAI_API_KEY=sk-...
#   SECRET_KEY=<random>
```

### 3. Deploy Frontend
```bash
# Option A: Static build
cd frontend && npm run build
# Deploy dist/ as static site

# Option B: Node service
# - Source: GitHub repo → frontend/
# - Build: Dockerfile at frontend/Dockerfile
# - Port: 5173
# - Env: VITE_API_URL=https://your-backend.koyeb.app
```

### 4. Run Migrations
```bash
# In backend service console:
alembic upgrade head
```

### 5. Import Data
```bash
python -m scripts.import_people
python -m scripts.ingest_rag_docs
python -m scripts.seed_demo  # Optional: for demo data
```

### 6. (Optional) Deploy ASR Worker
If GPU is needed for real-time ASR:
```bash
# Deploy scripts/run_local_gpu_asr.py as a separate GPU service
# Instance type: RTX-4000-SFF-ADA
# Port: 8001
# Set ASR_MODEL_NAME, HF_TOKEN in environment
```

## Alternative: Split Architecture
If Koyeb GPU limitations are problematic:
- **Koyeb**: Web app + API + PostgreSQL
- **Modal/RunPod/Lambda**: GPU ASR worker
- Keep the repo deployable with Koyeb-compatible defaults
