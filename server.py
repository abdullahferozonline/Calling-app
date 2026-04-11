from flask import Flask, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}

@socketio.on('register')
def register(data):
    user_id = data['id']
    users[user_id] = request.sid
    print(f"[+] {user_id} connected")

@socketio.on('call')
def call(data):
    target = data['to']
    if target in users:
        emit('incoming_call', {'from': data['from']}, room=users[target])
    else:
        emit('user_not_found')

@socketio.on('answer')
def answer(data):
    emit('call_answered', {'from': data['from']}, room=users[data['to']])

@socketio.on('offer')
def offer(data):
    emit('offer', data, room=users[data['to']])

@socketio.on('answer_sdp')
def answer_sdp(data):
    emit('answer_sdp', data, room=users[data['to']])

@socketio.on('ice_candidate')
def ice(data):
    emit('ice_candidate', data, room=users[data['to']])

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)
