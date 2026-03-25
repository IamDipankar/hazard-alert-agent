"""
ASR service — wraps the ai4bharat model for Bengali speech recognition.
Falls back to a mock transcriber if the model isn't available (no GPU).
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)

_model = None
_model_loaded = False
_model_failed = False


def _try_load_model():
    """Attempt to load the ASR model. Only tries once."""
    global _model, _model_loaded, _model_failed
    if _model_loaded or _model_failed:
        return

    try:
        import torch
        import torchaudio
        from transformers import AutoModel
        from backend.app.config import settings

        logger.info(f"Loading ASR model '{settings.ASR_MODEL_NAME}' ...")
        _model = AutoModel.from_pretrained(
            settings.ASR_MODEL_NAME,
            trust_remote_code=True,
            token=settings.HF_TOKEN,
            device_map="auto",
        )
        _model.eval()
        _model_loaded = True
        logger.info("ASR model loaded successfully.")
    except Exception as e:
        _model_failed = True
        logger.warning(f"ASR model not available — using mock transcriber. Error: {e}")


async def transcribe_audio(audio_bytes: bytes, sample_rate: int = 16000) -> str:
    """
    Transcribe audio bytes to Bengali text.
    Falls back to a mock response if model isn't available.
    """
    _try_load_model()

    if not _model_loaded:
        # Mock transcriber for demo without GPU
        return "হ্যাঁ, আমি শুনছি। আমাদের এলাকায় এখন বৃষ্টি হচ্ছে।"

    try:
        import torch
        import torchaudio

        audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        if audio_np.size == 0:
            return ""

        wav = torch.from_numpy(audio_np).unsqueeze(0)

        target_sr = 16000
        if sample_rate != target_sr:
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sr)
            wav = resampler(wav)

        with torch.inference_mode():
            out = _model(wav, "bn", "ctc")

        if isinstance(out, (list, tuple)):
            out = out[0]

        return str(out).strip()
    except Exception as e:
        logger.error(f"ASR transcription error: {e}")
        return "হ্যাঁ, আমি শুনছি।"
