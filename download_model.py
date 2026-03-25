"""
Download and cache the ASR model into the HuggingFace cache (HF_HOME).
Run this during build so the model is baked into the Docker image.

Usage:
    HF_TOKEN=hf_xxx python download_model.py
"""

import os
from huggingface_hub import snapshot_download

MODEL_NAME = "ai4bharat/indic-conformer-600m-multilingual"
HF_TOKEN = os.getenv("HF_TOKEN") or None


def main():
    print(f"Downloading model '{MODEL_NAME}' into HF cache ({os.getenv('HF_HOME', '~/.cache/huggingface')}) ...")
    snapshot_download(
        repo_id=MODEL_NAME,
        token=HF_TOKEN,
    )
    print("Model download complete.")


if __name__ == "__main__":
    main()
