import os
import time
from backend.utils.logger import logger

def generate_ai_video(image, audio, job_id=None):
    """
    Executes SadTalker synthesis for natural facial movement and perfect lip-sync.
    This bridges the backend container to the specialized SadTalker container.
    """
    if not job_id:
        import uuid
        job_id = str(uuid.uuid4())[:8]

    logger.info(f"🎭 [SADTALKER] Starting AI Synthesis for Job: {job_id}")

    # Paths inside the sadtalker container (assuming shared /app/output volume)
    # The image and audio paths provided should be accessible to the sadtalker container
    
    # We use subprocess or os.system to trigger the inference
    # Using --preprocess full for natural head movement
    cmd = f"""
    docker exec vartapravah_sadtalker python3 inference.py \
    --driven_audio {audio} \
    --source_image {image} \
    --result_dir /app/output/sadtalker_{job_id} \
    --still \
    --preprocess full \
    --enhancer gfpgan
    """

    # Note: --still is used for stability, but --preprocess full adds head movement
    # --enhancer gfpgan ensures high-quality face restoration

    os.system(cmd)

    # Polling for result
    result_path = f"/app/output/sadtalker_{job_id}"
    max_wait = 300 # 5 minutes
    elapsed = 0
    
    while elapsed < max_wait:
        if os.path.exists(result_path):
            # Find the .mp4 in the result_dir
            for root, dirs, files in os.walk(result_path):
                for file in files:
                    if file.endswith(".mp4"):
                        final_path = os.path.join(root, file)
                        logger.info(f"✅ [SADTALKER] Synthesis Complete: {final_path}")
                        return final_path
        
        time.sleep(5)
        elapsed += 5
        if elapsed % 30 == 0:
            logger.info(f"⏳ [SADTALKER] Synthesis in progress ({elapsed}s)...")

    logger.error(f"❌ [SADTALKER] Synthesis timed out after {max_wait}s")
    return None
