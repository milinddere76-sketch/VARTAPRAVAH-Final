import time
from services.news_fetcher import NewsFetcher
from services.script_generator import ScriptGenerator
from services.tts_engine import TTSEngine
from services.video_engine import VideoEngine
from utils.logger import logger

class BulletinManager:
    def __init__(self):
        self.fetcher = NewsFetcher()
        self.generator = ScriptGenerator()
        self.tts = TTSEngine()
        self.video = VideoEngine()

    def produce_bulletin(self):
        """Orchestrates the creation of a full news bulletin."""
        logger.info("🎬 Starting Bulletin Production...")
        
        # 1. Fetch News
        articles = self.fetcher.fetch_latest()
        if not articles:
            logger.warning("No news articles found. Skipping bulletin.")
            return

        for idx, article in enumerate(articles[:3]):  # Process top 3
            logger.info(f"📰 Processing Story {idx+1}: {article['title']}")
            
            # 2. Generate Marathi Script
            script = self.generator.generate_marathi_script(article['content'])
            
            # 3. TTS & Video Synthesis
            # This is where SadTalker/Wav2Lip would be triggered
            logger.info(f"✅ Story {idx+1} ready for synthesis.")
            
        logger.info("✨ Bulletin Production Cycle Complete.")

if __name__ == "__main__":
    manager = BulletinManager()
    manager.produce_bulletin()
