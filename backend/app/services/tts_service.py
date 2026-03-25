"""
TTS service — Google Cloud Text-to-Speech for Bengali voice synthesis.
Falls back to returning None (no audio) if credentials aren't configured.
"""

import logging
import base64
import hashlib
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Simple in-memory cache for repeated TTS phrases
_tts_cache: dict[str, str] = {}


async def synthesize_bengali(text: str) -> Optional[str]:
    """
    Synthesize Bengali text to speech using Google Cloud TTS.
    Returns a data URI (base64 audio) or None if TTS is not configured.
    """
    if not text or not text.strip():
        return None

    # Check cache
    cache_key = hashlib.md5(text.encode()).hexdigest()
    if cache_key in _tts_cache:
        return _tts_cache[cache_key]

    try:
        from google.cloud import texttospeech

        client = texttospeech.TextToSpeechClient()

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="bn-BD",
            name="bn-BD-Standard-A",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.95,
            pitch=0.0,
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )

        audio_b64 = base64.b64encode(response.audio_content).decode("utf-8")
        data_uri = f"data:audio/mp3;base64,{audio_b64}"

        # Cache it
        _tts_cache[cache_key] = data_uri
        return data_uri

    except Exception as e:
        logger.warning(f"TTS not available: {e}")
        return None
