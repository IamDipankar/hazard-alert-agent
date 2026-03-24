"""
ASR model loading and transcription utilities.
"""

import numpy as np
import torch
import torchaudio
from transformers import AutoModel

from config import MODEL_NAME, TARGET_SR, LANG_CODE, DECODE_STRATEGY, HF_TOKEN

# ── Resampler cache ─────────────────────────────────────────────────
_resampler_cache: dict[int, torchaudio.transforms.Resample] = {}


def _get_resampler(orig_sr: int) -> torchaudio.transforms.Resample:
    """Return a cached Resample transform for the given source sample rate."""
    if orig_sr not in _resampler_cache:
        _resampler_cache[orig_sr] = torchaudio.transforms.Resample(
            orig_freq=orig_sr, new_freq=TARGET_SR
        )
    return _resampler_cache[orig_sr]


# ── Model loading ───────────────────────────────────────────────────
_model = None


def load_model():
    """Load the ASR model (called once at startup)."""
    global _model
    print("Loading ASR model...")
    _model = AutoModel.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        token=HF_TOKEN,
        device_map="auto",
    )
    _model.eval()
    print("ASR model ready.")


def transcribe_int16_pcm(audio_bytes: bytes, sample_rate: int) -> str:
    """
    Transcribe raw 16-bit PCM audio bytes into text.

    Parameters
    ----------
    audio_bytes : bytes
        Raw int16 PCM audio data.
    sample_rate : int
        Sample rate of the incoming audio.

    Returns
    -------
    str
        The transcribed text.
    """
    if not audio_bytes:
        return ""

    audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    if audio_np.size == 0:
        return ""

    wav = torch.from_numpy(audio_np).unsqueeze(0)

    if sample_rate != TARGET_SR:
        wav = _get_resampler(sample_rate)(wav)

    with torch.inference_mode():
        out = _model(wav, LANG_CODE, DECODE_STRATEGY)

    if isinstance(out, (list, tuple)):
        out = out[0]

    return str(out).strip()