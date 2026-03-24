"""
Download and cache the ASR model locally.
Run this script during Docker build to bake the model into the image.

Usage:
    HF_TOKEN=hf_xxx python download_model.py
"""

import os
from transformers import AutoModel

MODEL_NAME = "ai4bharat/indic-conformer-600m-multilingual"
MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "/app/model_cache")
HF_TOKEN = os.getenv("HF_TOKEN") or None


def main():
    print(f"Downloading model '{MODEL_NAME}' into '{MODEL_CACHE_DIR}' ...")
    model = AutoModel.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        token=HF_TOKEN,
    )
    model.save_pretrained(MODEL_CACHE_DIR)
    print(f"Model saved to '{MODEL_CACHE_DIR}'.")


if __name__ == "__main__":
    main()
