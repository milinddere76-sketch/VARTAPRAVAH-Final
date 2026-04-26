import os
import time
from backend.utils.logger import logger

def generate_ai_video(image, audio, job_id=None):
    """
    Executes Wav2Lip synthesis for fast lip-sync.
    If it fails, falls back to generating a static video of the anchor with audio.
    """
    if not job_id:
        import uuid
        job_id = str(uuid.uuid4())[:8]

    logger.info(f"🎭 [WAV2LIP] Starting AI Synthesis for Job: {job_id}")

    result_path = f"/app/output/wav2lip_{job_id}.mp4"
    
    cmd = f"""
    docker exec vartapravah_wav2lip python3 inference.py \
    --checkpoint_path checkpoints/wav2lip_gan.pth \
    --face {image} \
    --audio {audio} \
    --outfile {result_path}
    """

    # Try Wav2Lip
    logger.info("Executing Wav2Lip...")
    exit_status = os.system(cmd)
    
    if exit_status == 0:
        max_wait = 180 # 3 minutes max for Wav2Lip
        elapsed = 0
        
        while elapsed < max_wait:
            if os.path.exists(result_path) and os.path.getsize(result_path) > 0:
                logger.info(f"✅ [WAV2LIP] Synthesis Complete: {result_path}")
                return result_path
            
            time.sleep(5)
            elapsed += 5
            if elapsed % 30 == 0:
                logger.info(f"⏳ [WAV2LIP] Synthesis in progress ({elapsed}s)...")

        logger.error(f"❌ [WAV2LIP] Synthesis timed out after {max_wait}s. Using static image fallback.")
    else:
        logger.error(f"❌ [WAV2LIP] Docker exec failed (status {exit_status}). Using static image fallback immediately.")

    
    # Fallback to static image
    fallback_path = f"/app/output/fallback_{job_id}.mp4"
    # -loop 1 loops the image, -i audio takes the audio. -shortest stops when audio is done.
    cmd_fallback = f'ffmpeg -y -loop 1 -i "{image}" -i "{audio}" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest "{fallback_path}"'
    
    logger.info("Executing FFmpeg Static Fallback...")
    os.system(cmd_fallback)
    
    if os.path.exists(fallback_path) and os.path.getsize(fallback_path) > 0:
        logger.info(f"✅ [FALLBACK] Static Synthesis Complete: {fallback_path}")
        return fallback_path
        
    logger.error("❌ [FALLBACK] Static video generation also failed.")
    return None
