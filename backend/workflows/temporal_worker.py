import asyncio
from datetime import timedelta
from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker, UnsandboxedWorkflowRunner

import concurrent.futures

from backend.services.news_fetcher import fetch_news
from backend.services.script_generator import generate_script
from backend.services.sadtalker_engine import generate_ai_video
from backend.services.video_engine import VideoEngine
from backend.utils.logger import logger
from backend import config

# ✅ IMPORT TTS INIT
from backend.services.tts_engine import init_tts


# =========================
# --- ACTIVITIES ---
# =========================

@activity.defn
def fetch_news_activity() -> list:
    logger.info("🎬 [ACTIVITY] Fetching News...")
    return fetch_news()

@activity.defn
def produce_script_activity(news: list) -> str:
    logger.info("🎬 [ACTIVITY] Generating Script...")
    return generate_script("\n".join(news))

@activity.defn
def render_video_activity(script: str, anchor_type: str = "female", headlines: list = None, is_breaking: bool = False) -> str:
    logger.info(f"🎬 [ACTIVITY] Rendering Video for {len(headlines) if headlines else 0} items...")
    from backend.workflows.video_worker import process_task_direct
    return process_task_direct(script, anchor_type, headlines, is_breaking)

@activity.defn
def transfer_video_activity(video_path: str) -> bool:
    oracle_ip = os.getenv("ORACLE_NODE_IP")
    if not oracle_ip:
        logger.warning("⚠️ [SYNC] ORACLE_NODE_IP not set. Skipping rsync.")
        return False
        
    import subprocess
    logger.info(f"📤 [SYNC] Transferring {video_path} to Oracle @ {oracle_ip}...")
    
    # 1. Sync to Oracle
    cmd = ["rsync", "-avz", video_path, f"ubuntu@{oracle_ip}:/home/ubuntu/videos/"]
    try:
        subprocess.run(cmd, check=True)
        logger.info("✅ [SYNC] Transfer successful")
        
        # 2. Cleanup (Strict Generate -> Transfer -> Delete policy)
        output_dir = os.path.dirname(video_path)
        for f in os.listdir(output_dir):
            f_path = os.path.join(output_dir, f)
            if f.endswith(".mp4") and f.startswith("final_bulletin_"):
                try:
                    os.remove(f_path)
                    logger.info(f"🧹 [CLEANUP] Deleted file: {f}")
                except Exception as e:
                    logger.warning(f"⚠️ [CLEANUP] Could not delete {f}: {e}")
        
        return True
    except Exception as e:
        logger.error(f"❌ [SYNC] Transfer failed: {e}")
        return False


# =========================
# --- WORKFLOWS ---
# =========================

@workflow.defn
class NewsProductionWorkflow:
    @workflow.run
    async def run(self, script: str, headlines: list, is_breaking: bool = False) -> str:
        # We no longer fetch or generate inside the workflow to avoid redundancy
        # but we keep the activities for manual triggers if needed.
        
        # 1. Render
        video_path = await workflow.execute_activity(
            render_video_activity,
            script,
            "female",
            headlines,
            is_breaking,
            start_to_close_timeout=timedelta(seconds=3600)
        )
        
        # 2. Sync & Cleanup (Final Recommended Flow)
        if video_path:
            await workflow.execute_activity(
                transfer_video_activity,
                video_path,
                start_to_close_timeout=timedelta(seconds=600)
            )
        
        return video_path


@workflow.defn
class StreamWorkflow:
    @workflow.run
    async def run(self):
        logger.info("📡 [WORKFLOW] Stream Monitoring Active")
        await asyncio.sleep(3600)


# =========================
# --- MAIN WORKER ---
# =========================

async def main():
    # 🔥 INIT TTS BEFORE WORKER STARTS
    logger.info("🔊 [TTS] Initializing in worker...")
    init_tts()
    logger.info("✅ [TTS] Ready in worker")

    # Connect to Temporal
    client = await Client.connect("temporal:7233")

    worker = Worker(
        client,
        task_queue="vartapravah-queue",
        workflows=[NewsProductionWorkflow, StreamWorkflow],
        activities=[fetch_news_activity, produce_script_activity, render_video_activity, transfer_video_activity],
        workflow_runner=UnsandboxedWorkflowRunner(),
        activity_executor=concurrent.futures.ThreadPoolExecutor(max_workers=5),
        max_concurrent_activities=5
    )

    logger.info("👷 [TEMPORAL] Worker started. Monitoring task queue...")
    await worker.run()


# =========================
# --- ENTRY POINT ---
# =========================

if __name__ == "__main__":
    asyncio.run(main())