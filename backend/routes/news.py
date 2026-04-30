from fastapi import APIRouter, HTTPException
from backend.services.news_fetcher import NewsFetcher
from backend.services.script_generator import ScriptGenerator
from temporalio.client import Client
from backend import config
from backend.utils.logger import logger

router = APIRouter(prefix="/news", tags=["news"])

@router.get("/latest")
def get_latest_news():
    """Fetches the latest news articles from the database."""
    fetcher = NewsFetcher()
    news = fetcher.fetch_all_categories()
    return {"status": "success", "categories": news}

@router.get("/force-generate")
async def force_generate_bulletin():
    try:
        # 1. Fetch news for the bulletin
        from backend.services.news_fetcher import fetch_news
        from backend.services.script_generator import generate_script
        
        headlines = fetch_news()
        script = generate_script(headlines)
        
        # 2. Connect to Temporal
        client = await Client.connect("temporal:7233")
        
        # 3. Start Workflow
        handle = await client.start_workflow(
            "NewsProductionWorkflow",
            args=[script, headlines, False],
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
