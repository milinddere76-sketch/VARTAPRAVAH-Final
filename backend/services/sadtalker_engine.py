import os
import time
import subprocess
from backend.utils.logger import logger
from backend.services.video_engine import get_asset_path

def generate_ai_video(image, audio, job_id=None):
    if not job_id:
        import uuid
        job_id = str(uuid.uuid4())[:8]

    # Handle image fallback
    if image and ("anchor_female" in str(image) or "anchor_male" in str(image)):
         image = get_asset_path(os.path.basename(image))

    logger.info(f"🎭 [WAV2LIP] Starting AI Synthesis for Job: {job_id}")

    # Ensure paths are clean
    image = str(image).strip()
    audio = str(audio).strip()
    result_path = f"/app/output/wav2lip_{job_id}.mp4"
    
    # 1. Find Wav2Lip Container
    try:
        container_cmd = ["docker", "ps", "--format", "{{.Names}}"]
        result = subprocess.run(container_cmd, capture_output=True, text=True)
        containers = [c.strip() for c in result.stdout.split('\n') if 'wav2lip' in c]
        
        if not containers:
            logger.error("❌ [WAV2LIP] Container not found!")
            return None
            
        wav2lip_container = containers[0]
        
        # 2. Run Wav2Lip via Docker Exec
        exec_cmd = [
            "docker", "exec", wav2lip_container, "python3", "inference.py",
            "--checkpoint_path", "checkpoints/wav2lip_gan.pth",
            "--face", image,
            "--audio", audio,
            "--outfile", result_path
        ]
        
        logger.info(f"Executing Wav2Lip in {wav2lip_container}...")
        res = subprocess.run(exec_cmd, capture_output=True, text=True)
        
        if res.returncode == 0:
            # Wait for file to appear (async in some setups)
            max_wait = 300 # 5 minutes for heavy rendering
            elapsed = 0
            while elapsed < max_wait:
                if os.path.exists(result_path) and os.path.getsize(result_path) > 0:
                    logger.info(f"✅ [WAV2LIP] Synthesis Complete: {result_path}")
                    return result_path
                time.sleep(5)
                elapsed += 5
                if elapsed % 30 == 0:
                    logger.info(f"⏳ [WAV2LIP] Rendering in progress ({elapsed}s)...")
            logger.error(f"❌ [WAV2LIP] Timeout waiting for {result_path}")
        else:
            logger.error(f"❌ [WAV2LIP] Docker exec failed: {res.stderr}")
            
    except Exception as e:
        logger.error(f"❌ [WAV2LIP] Execution Error: {e}")

    # --- FALLBACK: FFmpeg Static ---
    logger.info("⚠️ [WAV2LIP] Using static image fallback...")
    fallback_path = f"/app/output/fallback_{job_id}.mp4"
    
    fb_cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", image, "-i", audio,
        "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p", "-shortest", fallback_path
    ]
    
    try:
        fb_res = subprocess.run(fb_cmd, capture_output=True, text=True)
        if fb_res.returncode == 0 and os.path.exists(fallback_path):
            logger.info(f"✅ [FALLBACK] Static Synthesis Complete: {fallback_path}")
            return fallback_path
        else:
            logger.error(f"❌ [FALLBACK] FFmpeg failed: {fb_res.stderr}")
    except Exception as e:
        logger.error(f"❌ [FALLBACK] Unexpected Error: {e}")

    return None
