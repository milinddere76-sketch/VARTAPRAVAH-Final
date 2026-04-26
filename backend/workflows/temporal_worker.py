import asyncio
from datetime import timedelta
from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker

from services.news_fetcher import fetch_news
from services.script_generator import generate_script
from services.tts_engine import generate_audio
from services.sadtalker_engine import generate_ai_video
from services.video_engine import VideoEngine
from utils.logger import logger
import config

# --- ACTIVITIES ---

@activity.defn
async def fetch_news_activity() -> list:
    logger.info("🎬 [ACTIVITY] Fetching News...")
    return fetch_news()

@activity.defn
async def produce_script_activity(news: list) -> str:
    logger.info("🎬 [ACTIVITY] Generating Script...")
    return generate_script("\n".join(news))

@activity.defn
async def render_video_activity(script: str) -> str:
    logger.info("🎬 [ACTIVITY] Rendering Video...")
    # This combines TTS + Sadtalker + Final Composition
    # Simplified for the workflow orchestration
    from workflows.video_worker import process_task_direct
    return await process_task_direct(script)

# --- WORKFLOWS ---

@workflow.defn
class NewsProductionWorkflow:
    @workflow.run
    async def run(self) -> str:
        # 1. Fetch
        news = await workflow.execute_activity(
            fetch_news_activity,
            start_to_close_timeout=timedelta(seconds=60)
        )
        
        # 2. Generate
        script = await workflow.execute_activity(
            produce_script_activity,
            news,
            start_to_close_timeout=timedelta(seconds=120)
        )
        
        # 3. Render
        video_path = await workflow.execute_activity(
            render_video_activity,
            script,
            start_to_close_timeout=timedelta(seconds=600) # 10 mins for AI
        )
        
        return video_path

@workflow.defn
class StreamWorkflow:
    @workflow.run
    async def run(self):
        # This workflow monitors the stream status and self-heals
        # Logic to be expanded based on specific relay feedback
        logger.info("📡 [WORKFLOW] Stream Monitoring Active")
        await asyncio.sleep(3600) # Keep alive for 1 hour

# --- WORKER ---

async def main():
    # Connect to Temporal Server (assumed running in infra)
    client = await Client.connect("temporal:7233")
    
    worker = Worker(
        client,
        task_queue="vartapravah-queue",
        workflows=[NewsProductionWorkflow, StreamWorkflow],
        activities=[fetch_news_activity, produce_script_activity, render_video_activity]
    )
    
    logger.info("👷 [TEMPORAL] Worker started. Monitoring task queue...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
