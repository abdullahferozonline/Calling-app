# Calling App

A small two-person video calling app using WebRTC for media and Flask-SocketIO for signaling. Audio and video are sent peer-to-peer; the Python server only coordinates the connection.

## Run locally

```bash
python -m venv .venv
. .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python server.py
```

Open `http://localhost:5000` in two browser windows and enter the same room name. Camera and microphone access requires HTTPS when deployed (localhost is allowed for local testing).

## Deploy on a Termux host

This project can be served from the Termux setup described in [ZERO-RUPEE-TERMUX-WEBSITE-HOSTING](https://github.com/abdullahferozonline/ZERO-RUPEE-TERMUX-WEBSITE-HOSTING). Run the app behind Caddy so the public URL uses HTTPS:

```bash
pkg update && pkg install python
pip install -r requirements.txt
python server.py
```

Configure Caddy to reverse proxy your HTTPS hostname to `127.0.0.1:5000` and keep WebSocket support enabled (Caddy's `reverse_proxy` does this automatically). Do not commit DuckDNS tokens or other secrets. Use a strong `SECRET_KEY` environment variable in production.

## Notes

- The demo allows a maximum of two participants per room.
- Both callers need a browser with WebRTC support and camera/microphone permission.
- Some restrictive mobile networks need a TURN server for calls; the included public STUN server is not a guarantee of connectivity.
- `/health` can be used by a host or monitor to verify the process is running.
