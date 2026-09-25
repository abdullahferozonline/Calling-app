from __future__ import annotations

import os
from typing import Any

from flask import Flask, jsonify, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# Keep the demo intentionally small: one room represents one private two-person call.
rooms: dict[str, set[str]] = {}


@app.get("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "calling-app"})


@socketio.on("join")
def handle_join(data: Any):
    room = str((data or {}).get("room", "")).strip()[:64]
    if not room:
        emit("error", {"message": "A room name is required."})
        return

    members = rooms.setdefault(room, set())
    if len(members) >= 2:
        emit("room-full", {"message": "This room already has two people."})
        return

    sid = getattr(__import__("flask").request, "sid")
    join_room(room)
    members.add(sid)
    emit("joined", {"room": room, "count": len(members)})
    emit("peer-joined", {"room": room}, to=room, include_self=False)


@socketio.on("signal")
def handle_signal(data: Any):
    data = data or {}
    room = str(data.get("room", "")).strip()
    if room not in rooms:
        return
    emit("signal", {"type": data.get("type"), "payload": data.get("payload")}, to=room, include_self=False)


@socketio.on("leave")
def handle_leave(data: Any):
    _remove_from_room(str((data or {}).get("room", "")).strip(), getattr(__import__("flask").request, "sid"))


@socketio.on("disconnect")
def handle_disconnect():
    sid = getattr(__import__("flask").request, "sid")
    for room in list(rooms):
        _remove_from_room(room, sid)


def _remove_from_room(room: str, sid: str):
    members = rooms.get(room)
    if not members or sid not in members:
        return
    members.remove(sid)
    leave_room(room)
    emit("peer-left", {"room": room}, to=room)
    if not members:
        rooms.pop(room, None)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    socketio.run(app, host="0.0.0.0", port=port)
