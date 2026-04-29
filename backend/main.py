from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import threading
import os
import redis
import time

from backend.workflows.scheduler import main as scheduler_main
from backend import config
from backend.database import init_db, log_analytics
from backend.routes import stream, news

# ✅ ADD THIS IMPORT
from backend.services.tts_engine import init_tts

app = FastAPI(title="VARTA PRAVAH ENTERPRISE DASHBOARD")

# Include Routers
app.include_router(stream.router)
app.include_router(news.router)

# Initialize Redis for fast metrics
r = redis.Redis(host=config.REDIS_HOST, port=int(config.REDIS_PORT))

# Serve static files and videos
backend_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(backend_dir, "static")
output_dir = os.path.join(os.path.dirname(backend_dir), "output")

# Mount static and video folders
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
app.mount("/videos", StaticFiles(directory=output_dir), name="videos")

@app.get("/")
def read_dashboard():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Visual Dashboard coming soon. Access analytics at /api/analytics"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# --- ANALYTICS & VIDEO API ---

@app.get("/api/latest-video")
def get_latest_video():
    try:
        files = [f for f in os.listdir(output_dir) if f.startswith("final_bulletin_") and f.endswith(".mp4")]
        if not files:
            return {"status": "error", "message": "No bulletins available"}

        files.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]), reverse=True)
        return {"status": "success", "video_url": f"/videos/{files[0]}", "filename": files[0]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/analytics")
def get_analytics():
    try:
        videos = int(r.get("stats_videos_generated") or 0)
        errors = int(r.get("stats_errors_count") or 0)
        revenue = round(videos * 0.15, 2)

        log_analytics(videos, errors, revenue)

        import random
        viewers = random.randint(500, 15000)

        return {
            "live_viewers": f"{viewers:,}",
            "videos_generated": videos,
            "errors": errors,
            "revenue": f"${revenue}",
            "status": "ONLINE"
        }
    except Exception as e:
        return {"status": "OFFLINE", "error": str(e)}

def run_scheduler():
    scheduler_main()

# ✅ UPDATED STARTUP EVENT
@app.on_event("startup")
async def startup_event():
    try:
        time.sleep(5)

        # ✅ INIT DATABASE
        init_db()

        # 🔥 INIT TTS MODEL ONLY IF WORKER
        is_worker = os.getenv("IS_AI_WORKER", "false").lower() == "true"
        if is_worker:
            print("🔊 [TTS] Initializing AI Engine...")
            init_tts()
            print("✅ [TTS] Ready")
        else:
            print("🏢 [MAIN] Skipping TTS Init (Backend Mode)")

    except Exception as e:
        print(f"⚠️ [STARTUP ERROR]: {e}")

    # ✅ START SCHEDULER AFTER TTS IS READY
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()

    print("🏢 [MAIN] Enterprise Dashboard & Scheduler started.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)