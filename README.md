# Bengali ASR Demo

Real-time Bengali speech-to-text using [ai4bharat/indic-conformer-600m-multilingual](https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual).  
Hold the microphone button, speak in Bengali, and see the transcript update live.

## Project Structure

```
├── config.py          # Constants & environment settings
├── asr_model.py       # Model loading & transcription logic
├── app.py             # FastAPI routes & WebSocket handler
├── templates/
│   └── index.html     # Frontend UI
├── run_server.py      # Entry point (uvicorn + optional ngrok)
├── requirements.txt   # Python dependencies
└── .env               # Environment variables (HF_TOKEN, NGROK_AUTHTOKEN, etc.)
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file (or set environment variables):

```env
HF_TOKEN=hf_your_token_here
NGROK_AUTHTOKEN=your_ngrok_token    # optional, for tunneling
HOST=0.0.0.0                        # optional, default 0.0.0.0
PORT=8000                            # optional, default 8000
```

### 3. Run the server

```bash
python run_server.py
```

Then open `http://localhost:8000` in your browser.

## Colab Usage

If `NGROK_AUTHTOKEN` is set, the server will automatically create an ngrok tunnel and print the public URL. This is useful for Google Colab where localhost is not directly accessible.

## How It Works

1. **Frontend** captures microphone audio as 16-bit PCM via WebSocket
2. **Backend** accumulates audio chunks and runs the ASR model every ~2 seconds for intermediate results
3. On release, the full audio is transcribed and returned as the final result
