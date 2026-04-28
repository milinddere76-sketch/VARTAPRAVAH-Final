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
def render_video_activity(script: str) -> str:
    logger.info("🎬 [ACTIVITY] Rendering Video...")

    # 🚨 SAFETY CHECK (VERY IMPORTANT)
    if not script or not script.strip():
        raise Exception("❌ Empty script received")

    # This internally uses TTS → SadTalker → FFmpeg
    from backend.workflows.video_worker import process_task_direct
    return process_task_direct(script)


# =========================
# --- WORKFLOWS ---
# =========================

@workflow.defn
class NewsProductionWorkflow:
    @workflow.run
    async def run(self) -> str:

        news = await workflow.execute_activity(
            fetch_news_activity,
            start_to_close_timeout=timedelta(seconds=60)
        )

        script = await workflow.execute_activity(
            produce_script_activity,
            news,
            start_to_close_timeout=timedelta(seconds=120)
        )

        video_path = await workflow.execute_activity(
            render_video_activity,
            script,
            start_to_close_timeout=timedelta(seconds=3600)
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
        activities=[fetch_news_activity, produce_script_activity, render_video_activity],
        workflow_runner=UnsandboxedWorkflowRunner(),
        activity_executor=concurrent.futures.ThreadPoolExecutor(max_workers=5)
    )

    logger.info("👷 [TEMPORAL] Worker started. Monitoring task queue...")
    await worker.run()


# =========================
# --- ENTRY POINT ---
# =========================

if __name__ == "__main__":
    asyncio.run(main())