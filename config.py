"""
Application configuration and constants.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── ASR Model Settings ──────────────────────────────────────────────
MODEL_NAME = "ai4bharat/indic-conformer-600m-multilingual"
TARGET_SR = 16000
LANG_CODE = "bn"
DECODE_STRATEGY = "ctc"

# ── Server Settings ─────────────────────────────────────────────────
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# ── Tokens ──────────────────────────────────────────────────────────
HF_TOKEN = os.getenv("HF_TOKEN") or None
NGROK_AUTHTOKEN = os.getenv("NGROK_AUTHTOKEN") or None

# ── Streaming Settings ──────────────────────────────────────────────
UPDATE_EVERY_SECONDS = 2.0
