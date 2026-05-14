"""SocketIO namespace for streaming AutoML training updates.

Client flow:
    const sock = io('http://localhost:5000/training', { auth: { token } });
    sock.emit('subscribe', { jobId });
    sock.on('job:update', (p) => ...);
    sock.on('job:done',   (p) => ...);
"""
from flask_socketio import join_room, leave_room, emit
import jwt as pyjwt
from utils.jwt_utils import decode_token

NS = "/training"


def register_training_namespace(socketio):
    @socketio.on("connect", namespace=NS)
    def _connect(auth):
        token = (auth or {}).get("token") if isinstance(auth, dict) else None
        if not token:
            return False  # reject
        try:
            decode_token(token)
        except pyjwt.PyJWTError:
            return False
        emit("connected", {"ok": True})

    @socketio.on("subscribe", namespace=NS)
    def _subscribe(data):
        job_id = (data or {}).get("jobId")
        if not job_id:
            return
        join_room(f"job:{job_id}")
        emit("subscribed", {"jobId": job_id})

    @socketio.on("unsubscribe", namespace=NS)
    def _unsubscribe(data):
        job_id = (data or {}).get("jobId")
        if job_id:
            leave_room(f"job:{job_id}")
