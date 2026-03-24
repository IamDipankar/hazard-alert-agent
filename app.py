"""
FastAPI application — HTTP and WebSocket endpoints.
"""

import json
import os
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from config import UPDATE_EVERY_SECONDS
from asr_model import load_model, transcribe_int16_pcm

# ── Initialise app & templates ──────────────────────────────────────
app = FastAPI(title="Bengali ASR Demo")

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# ── Startup event ───────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    """Load the ASR model when the server starts."""
    load_model()


# ── Routes ──────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main UI page."""
    return templates.TemplateResponse(request=request, name="index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint that receives streaming audio and returns
    intermediate + final transcriptions.
    """
    await websocket.accept()

    sample_rate: Optional[int] = None
    all_audio = bytearray()
    pending_audio = bytearray()
    bytes_per_second = None

    await websocket.send_json({
        "status": "Connected. Hold the button and start speaking in Bengali."
    })

    try:
        while True:
            message = await websocket.receive()

            # ── Text (JSON control messages) ────────────────────────
            if "text" in message and message["text"] is not None:
                payload = json.loads(message["text"])
                event = payload.get("event")

                if event == "start":
                    sample_rate = int(payload["sample_rate"])
                    bytes_per_second = sample_rate * 2
                    all_audio = bytearray()
                    pending_audio = bytearray()
                    await websocket.send_json({"status": "Mic started. Speak now..."})

                elif event == "stop":
                    if sample_rate and len(all_audio) > 0:
                        transcript = transcribe_int16_pcm(bytes(all_audio), sample_rate)
                        await websocket.send_json({"text": transcript, "status": "Done."})
                    else:
                        await websocket.send_json({"status": "No audio captured."})

            # ── Binary (raw PCM audio chunks) ───────────────────────
            if "bytes" in message and message["bytes"] is not None:
                chunk = message["bytes"]
                all_audio.extend(chunk)
                pending_audio.extend(chunk)

                if (
                    sample_rate
                    and bytes_per_second
                    and len(pending_audio) >= int(bytes_per_second * UPDATE_EVERY_SECONDS)
                ):
                    transcript = transcribe_int16_pcm(bytes(all_audio), sample_rate)
                    await websocket.send_json({"text": transcript, "status": "Transcribing..."})
                    pending_audio = bytearray()

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as exc:
        await websocket.send_json({"error": str(exc)})
