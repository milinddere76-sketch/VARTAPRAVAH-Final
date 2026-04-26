import redis
import json
import time
import os
from backend import config
from backend.services.tts_engine import init_tts, generate_audio
from backend.services.sadtalker_engine import generate_ai_video
from backend.services.video_engine import VideoEngine
from backend.utils.logger import logger

# Dedicated SadTalker Worker Configuration
r = redis.Redis(host=config.REDIS_HOST, port=int(config.REDIS_PORT))
video_engine = VideoEngine()

os.makedirs(config.OUTPUT_DIR, exist_ok=True)

logger.info("🎭 [SADTALKER-WORKER] Dedicated AI Face Engine starting...")
init_tts()

async def process_task_direct(script: str, anchor_type: str = "female", headlines: list = None, is_breaking: bool = False):
    if headlines is None:
        headlines = []
    
    task_id = int(time.time())
    logger.info(f"🎙️ [SADTALKER-WORKER] Processing Task {task_id} for {anchor_type.upper()}...")

    # 1. Neural TTS Synthesis
    audio_file = os.path.join(config.OUTPUT_DIR, f"audio_{task_id}.mp3")
    generate_audio(script, audio_file)

    if not os.path.exists(audio_file):
        logger.error("❌ [TTS] Failed to generate audio")
        r.incr("stats_errors_count")
        raise Exception("TTS Generation Failed")

    # 2. SadTalker AI Face Generation
    face_image = os.path.join(config.ASSETS_DIR, f"anchor_{anchor_type}.jpg")
    if not os.path.exists(face_image):
        alt_image = os.path.join(config.ASSETS_DIR, f"{anchor_type}_anchor.png")
        if os.path.exists(alt_image):
            face_image = alt_image
        else:
            # Extreme fallback: use any jpg/png in the assets folder
            for f in os.listdir(config.ASSETS_DIR):
                if f.endswith(".jpg") or f.endswith(".png"):
                    face_image = os.path.join(config.ASSETS_DIR, f)
                    break
    
    logger.info(f"Using face image: {face_image}")
    
    # This function handles full synthesis
    sadtalker_video = generate_ai_video(face_image, audio_file, task_id)
    
    if sadtalker_video and os.path.exists(sadtalker_video):
        # 3. Final Video Composition
        final_video_name = f"final_bulletin_{task_id}.mp4"
        final_path = video_engine.generate_video(sadtalker_video, headlines, final_video_name, is_breaking)
        
        if final_path and os.path.exists(final_path):
            logger.info(f"✅ [COMPLETED] Bulletin Ready: {final_path}")
            r.rpush("ready_videos", final_path)
            r.incr("stats_videos_generated")
            return final_path
        else:
            logger.error("❌ [COMPOSITION] Final branding failed")
            r.incr("stats_errors_count")
            raise Exception("Video Composition Failed")
    else:
        logger.error("❌ [SADTALKER] AI synthesis failed or timed out")
        r.incr("stats_errors_count")
        raise Exception("SadTalker Generation Failed")

