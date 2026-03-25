"""
Standalone ASR worker for GPU inference.
Loads the ai4bharat model and exposes a simple HTTP endpoint for transcription.

Usage:
    python scripts/run_local_gpu_asr.py

This is meant to run on a GPU machine separately from the main API.
"""

import os
import sys
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

MODEL_NAME = os.getenv("ASR_MODEL_NAME", "ai4bharat/indic-conformer-600m-multilingual")
HF_TOKEN = os.getenv("HF_TOKEN")
DEVICE = os.getenv("ASR_DEVICE", "cuda")
PORT = int(os.getenv("ASR_PORT", "8001"))

_model = None


def load_model():
    global _model
    from transformers import AutoModel
    print(f"Loading ASR model '{MODEL_NAME}' on {DEVICE}...")
    _model = AutoModel.from_pretrained(
        MODEL_NAME, trust_remote_code=True, token=HF_TOKEN, device_map="auto"
    )
    _model.eval()
    print("✅ ASR model loaded and ready.")


def transcribe(audio_bytes: bytes, sample_rate: int = 16000) -> str:
    import torchaudio

    audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    if audio_np.size == 0:
        return ""

    wav = torch.from_numpy(audio_np).unsqueeze(0)
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        wav = resampler(wav)

    with torch.inference_mode():
        out = _model(wav, "bn", "ctc")
    if isinstance(out, (list, tuple)):
        out = out[0]
    return str(out).strip()


def main():
    from fastapi import FastAPI, UploadFile, File, Form
    import uvicorn

    app = FastAPI(title="Bengali ASR Worker")
    load_model()

    @app.get("/health")
    async def health():
        return {"status": "ok", "model": MODEL_NAME, "device": DEVICE}

    @app.post("/transcribe")
    async def transcribe_endpoint(
        audio: UploadFile = File(...),
        sample_rate: int = Form(16000),
    ):
        audio_bytes = await audio.read()
        text = transcribe(audio_bytes, sample_rate)
        return {"text": text}

    uvicorn.run(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
