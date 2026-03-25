"""
Application configuration — loads all settings from environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # ── App ─────────────────────────────────────────────────────────
    APP_BASE_URL: str = "http://localhost:8000"
    SECRET_KEY: str = "change-me-to-a-random-string"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── Database ────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/hazard_alert"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/hazard_alert"
    PGVECTOR_ENABLED: bool = True

    # ── Redis ───────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── OpenAI ──────────────────────────────────────────────────────
    OPENAI_API_KEY: Optional[str] = None

    # ── Google Cloud TTS ────────────────────────────────────────────
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_TTS_PROJECT_ID: Optional[str] = None

    # ── ASR ──────────────────────────────────────────────────────────
    ASR_MODEL_NAME: str = "ai4bharat/indic-conformer-600m-multilingual"
    ASR_DEVICE: str = "cuda"
    ASR_BATCH_SIZE: int = 1
    HF_TOKEN: Optional[str] = None

    # ── Map ──────────────────────────────────────────────────────────
    MAPBOX_TOKEN: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
