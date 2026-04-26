from fastapi import APIRouter, HTTPException
from services.news_fetcher import NewsFetcher
from services.script_generator import ScriptGenerator
from temporalio.client import Client
import config
from utils.logger import logger

router = APIRouter(prefix="/news", tags=["news"])

@router.get("/latest")
def get_latest_news():
    """Fetches the latest news articles from the database."""
    fetcher = NewsFetcher()
    news = fetcher.fetch_all_categories()
    return {"status": "success", "categories": news}

@router.post("/force-generate")
async def force_generate_bulletin():
    """Immediately triggers a NewsProductionWorkflow in Temporal."""
    try:
        # Connect to Temporal
        client = await Client.connect("temporal:7233")
        
        # Start Workflow
        handle = await client.start_workflow(
            "NewsProductionWorkflow",
            id=f"force-bulletin-{int(config.time.time())}",
            task_queue="vartapravah-queue",
        )
        
        logger.info(f"🚀 [CONTROL-PANEL] Force-bulletin triggered: {handle.id}")
        return {"status": "success", "workflow_id": handle.id, "message": "Bulletin generation initiated"}
    except Exception as e:
        logger.error(f"❌ [CONTROL-PANEL] Force-generate failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-script")
def generate_script_api(article_text: str):
    """Generates a Marathi news script for a given article."""
    generator = ScriptGenerator()
    script = generator.generate_marathi_script(article_text)
    return {"status": "success", "script": script}
