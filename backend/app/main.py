"""
FastAPI application entry point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.api import health, people, events, campaigns, calls, analytics, map

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Hazard Alert Agent starting up...")
    logger.info(f"   Environment: {settings.ENVIRONMENT}")
    logger.info(f"   OpenAI configured: {bool(settings.OPENAI_API_KEY)}")
    logger.info(f"   Google TTS configured: {bool(settings.GOOGLE_APPLICATION_CREDENTIALS)}")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Hazard Alert Agent API",
    description="Bengali disaster early-warning voice AI system for Bangladesh",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api")
app.include_router(people.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(campaigns.router, prefix="/api")
app.include_router(calls.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(map.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": "Hazard Alert Agent",
        "version": "1.0.0",
        "description": "Bengali disaster early-warning voice AI system",
    }
