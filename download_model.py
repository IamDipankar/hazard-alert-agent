"""
Download and cache the ASR model locally.
Run this script during build (Docker or Koyeb buildpack) to bake the model into the image/slug.

Uses snapshot_download() to download raw files without instantiating the model,
which avoids issues with ONNX models that lack standard PyTorch parameters.

Usage:
    HF_TOKEN=hf_xxx python download_model.py
"""

import os
from huggingface_hub import snapshot_download

MODEL_NAME = "ai4bharat/indic-conformer-600m-multilingual"
MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_cache"))
HF_TOKEN = os.getenv("HF_TOKEN") or None


def main():
    print(f"Downloading model '{MODEL_NAME}' into '{MODEL_CACHE_DIR}' ...")
    os.makedirs(MODEL_CACHE_DIR, exist_ok=True)
    snapshot_download(
        repo_id=MODEL_NAME,
        local_dir=MODEL_CACHE_DIR,
        token=HF_TOKEN,
    )
    print(f"Model saved to '{MODEL_CACHE_DIR}'.")


if __name__ == "__main__":
    main()
