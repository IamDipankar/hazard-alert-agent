"""
Entry point — starts the Uvicorn server and optionally opens an ngrok tunnel.
"""

import uvicorn
from config import HOST, PORT, NGROK_AUTHTOKEN


def main():
    # ── Optional ngrok tunnel (useful when running in Colab) ────────
    if NGROK_AUTHTOKEN:
        try:
            from pyngrok import ngrok

            ngrok.set_auth_token(NGROK_AUTHTOKEN)

            # Kill any leftover tunnels
            try:
                ngrok.kill()
            except Exception:
                pass

            public_url = ngrok.connect(PORT, bind_tls=True).public_url
            print(f"\n🌐  ngrok tunnel is live:")
            print(f"    {public_url}\n")
        except ImportError:
            print("pyngrok not installed — skipping ngrok tunnel.")
    else:
        print(f"\n🚀  Starting server at http://{HOST}:{PORT}\n")

    # ── Start Uvicorn ───────────────────────────────────────────────
    uvicorn.run("app:app", host=HOST, port=PORT, reload=False)


if __name__ == "__main__":
    main()