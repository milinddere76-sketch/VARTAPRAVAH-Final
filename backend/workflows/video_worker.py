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

while True:
    # Listening for high-fidelity synthesis tasks
    data = r.blpop(config.QUEUE_NAME, timeout=5)

    if not data:
        time.sleep(1)
        continue

    try:
        task = json.loads(data[1])
        task_id = task["id"]
        script = task["script"]
        anchor_type = task.get("anchor_type", "female")
        headlines = task.get("headlines", [])
        is_breaking = task.get("is_breaking", False)
        
        logger.info(f"🎙️ [SADTALKER-WORKER] Processing Task {task_id} for {anchor_type.upper()}...")

        # 1. Neural TTS Synthesis (Perfectly synced Marathi audio)
        audio_file = os.path.join(config.OUTPUT_DIR, f"audio_{task_id}.mp3")
        generate_audio(script, audio_file)

        if not os.path.exists(audio_file):
            logger.error("❌ [TTS] Failed to generate audio")
            r.incr("stats_errors_count")
            continue

        # 2. SadTalker AI Face Generation (Dynamic facial movement + Lip sync)
        face_image = os.path.join(config.ASSETS_DIR, f"anchor_{anchor_type}.jpg")
        
        # This function now handles full synthesis and returns the final MP4 path
        sadtalker_video = generate_ai_video(face_image, audio_file, task_id)
        
        if sadtalker_video and os.path.exists(sadtalker_video):
            # 3. Final Video Composition (Ticker + Flash Headlines)
            final_video_name = f"final_bulletin_{task_id}.mp4"
            final_path = video_engine.generate_video(sadtalker_video, headlines, final_video_name, is_breaking)
            
            if final_path and os.path.exists(final_path):
                logger.info(f"✅ [COMPLETED] Bulletin Ready: {final_path}")
                r.rpush("ready_videos", final_path)
                r.incr("stats_videos_generated")
            else:
                logger.error("❌ [COMPOSITION] Final branding failed")
                r.incr("stats_errors_count")
        else:
            logger.error("❌ [SADTALKER] AI synthesis failed or timed out")
            r.incr("stats_errors_count")

    except Exception as e:
        logger.error(f"🚨 [CRITICAL] Worker Error: {e}")
        r.incr("stats_errors_count")
        time.sleep(2)
