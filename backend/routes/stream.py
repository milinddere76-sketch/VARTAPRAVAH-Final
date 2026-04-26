from fastapi import APIRouter
import subprocess
import os

router = APIRouter(prefix="/stream", tags=["streaming"])

@router.get("/start")
def start_stream():
    """Starts the RTMP stream container."""
    try:
        subprocess.run(["docker", "start", "vartapravah_streamer"], check=True, timeout=10)
        return {"status": "started", "message": "Streamer container initiated"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/stop")
def stop_stream():
    """Stops the RTMP stream container."""
    try:
        subprocess.run(["docker", "stop", "vartapravah_streamer"], check=True, timeout=10)
        return {"status": "stopped", "message": "Streamer container halted"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
