# ── Build stage ──────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# System deps for audio processing
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

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

# Clear the build-time token from the environment
ENV HF_TOKEN=""

# ── Runtime stage ────────────────────────────────────────────────────
FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code and cached model
COPY --from=builder /app /app

# Koyeb sets PORT via env var; default to 8000
ENV PORT=8000
ENV HOST=0.0.0.0

EXPOSE 8000

CMD ["python", "run_server.py"]
