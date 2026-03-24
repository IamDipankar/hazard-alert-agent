# ── Build stage ──────────────────────────────────────────────────────
# Use NVIDIA CUDA base image for GPU support on Koyeb
FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04 AS builder

# Prevent interactive prompts during apt install
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.11 and system deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.11 python3.11-venv python3.11-dev python3-pip \
        ffmpeg curl && \
    ln -sf /usr/bin/python3.11 /usr/bin/python && \
    ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python -m pip install --no-cache-dir --upgrade pip

WORKDIR /app

# Install Python deps first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Download the model during build so it's baked into the image
ARG HF_TOKEN
ENV HF_TOKEN=${HF_TOKEN}
RUN python download_model.py

# Clear the build-time token
ENV HF_TOKEN=""

# ── Runtime stage ────────────────────────────────────────────────────
FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.11 python3.11-venv \
        ffmpeg && \
    ln -sf /usr/bin/python3.11 /usr/bin/python && \
    ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages and app from builder
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/lib/python3/dist-packages /usr/lib/python3/dist-packages
COPY --from=builder /usr/lib/python3.11 /usr/lib/python3.11
COPY --from=builder /app /app

# Make sure pip-installed packages are on PATH
ENV PATH="/usr/local/bin:${PATH}"
ENV PYTHONPATH="/usr/local/lib/python3.11/dist-packages:${PYTHONPATH}"

# Koyeb sets PORT via env var; default to 8000
ENV PORT=8000
ENV HOST=0.0.0.0

# Tell PyTorch to use CUDA
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

EXPOSE 8000

CMD ["python", "run_server.py"]
