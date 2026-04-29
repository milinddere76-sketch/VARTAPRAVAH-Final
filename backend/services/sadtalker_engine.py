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

    # Ensure paths are clean
    # IMPORTANT: We must pass paths that the TARGET (Wav2Lip) container understands
    image_filename = os.path.basename(str(image))
    wav2lip_face_path = f"/app/assets/{image_filename}" 
    
    audio_filename = os.path.basename(str(audio))
    wav2lip_audio_path = f"/app/output/{audio_filename}" 
    
    result_path = f"/app/output/wav2lip_{job_id}.mp4"
    
    # 1. Find Wav2Lip Container
    try:
        docker_bin = "/usr/bin/docker" if os.path.exists("/usr/bin/docker") else "docker"
        
        # Try exact name first
        container_cmd = [docker_bin, "ps", "-q", "--filter", "name=vartapravah_wav2lip"]
        result = subprocess.run(container_cmd, capture_output=True, text=True)
        container_ids = [c.strip() for c in result.stdout.split('\n') if c.strip()]
        
        if container_ids:
            wav2lip_container = container_ids[0]
            logger.info(f"Found exact Wav2Lip container: {wav2lip_container}")
        else:
            # Fallback to fuzzy match
            container_cmd = [docker_bin, "ps", "--format", "{{.Names}}"]
            result = subprocess.run(container_cmd, capture_output=True, text=True)
            containers = [c.strip() for c in result.stdout.split('\n') if 'wav2lip' in c]
            
            if not containers:
                logger.error("❌ [WAV2LIP] Container not found!")
                return None
            wav2lip_container = containers[0]
            logger.warning(f"Using fuzzy-matched Wav2Lip container: {wav2lip_container}")
        
        # 2. Run Wav2Lip via Docker Exec
        exec_cmd = [
            docker_bin, "exec", wav2lip_container, "python3", "/app/Wav2Lip/inference.py",
            "--checkpoint_path", "/app/Wav2Lip/checkpoints/wav2lip_gan.pth",
            "--face", wav2lip_face_path,
            "--audio", wav2lip_audio_path,
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

    # --- FALLBACK 1: Sync Labs API ---
    from backend import config
    if config.SYNC_API_KEY:
        try:
            logger.info(f"🚀 [FALLBACK] Attempting Sync Labs API for Job {job_id}...")
            synclabs_video = generate_synclabs_video(image, audio, job_id)
            if synclabs_video and os.path.exists(synclabs_video):
                logger.info(f"✅ [SYNC-LABS] Cloud Synthesis Complete: {synclabs_video}")
                return synclabs_video
        except Exception as e:
            logger.error(f"❌ [SYNC-LABS] API Call Failed: {e}")

    # --- FALLBACK 2: FFmpeg Static ---
    logger.info(f"⚠️ [PIPELINE] Using final static image fallback for Job {job_id}...")
    fallback_path = f"/app/output/fallback_{job_id}.mp4"
    
    # Ensure even dimensions for libx264 (720p)
    fb_cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(image), "-i", str(audio),
        "-vf", "scale=854:480",
        "-c:v", "libx264", "-preset", "ultrafast", "-tune", "stillimage",
        "-crf", "28", "-threads", "1", 
        "-c:a", "aac", "-b:a", "128k", "-pix_fmt", "yuv420p", "-shortest", 
        fallback_path
    ]
    
    try:
        fb_res = subprocess.run(fb_cmd, capture_output=True, text=True, timeout=300)
        if fb_res.returncode == 0 and os.path.exists(fallback_path) and os.path.getsize(fallback_path) > 1000:
            logger.info(f"✅ [FALLBACK] Static Synthesis Complete: {fallback_path}")
            return fallback_path
        else:
            logger.error(f"❌ [FALLBACK] FFmpeg failed or produced empty file: {fb_res.stderr}")
    except Exception as e:
        logger.error(f"❌ [FALLBACK] Unexpected Error: {e}")

    return None

def generate_synclabs_video(image_path, audio_path, job_id):
    """
    Calls Sync Labs API to generate lip-synced video.
    Note: Requires Sync Labs API key in config.
    """
    import requests
    from backend import config
    
    API_KEY = config.SYNC_API_KEY
    BASE_URL = "https://api.synclabs.so/v2"
    HEADERS = {"x-api-key": API_KEY}
    
    try:
        # 1. Upload Assets (Sync Labs requires public URLs or direct uploads via signed URLs)
        def upload_file(file_path):
            # Step A: Get Signed URL
            res = requests.post(f"{BASE_URL}/uploads", headers=HEADERS)
            if res.status_code != 201:
                raise Exception(f"Failed to get upload URL: {res.text}")
            
            data = res.json()
            upload_url = data["url"]
            asset_id = data["id"]
            
            # Step B: Put File
            with open(file_path, "rb") as f:
                put_res = requests.put(upload_url, data=f)
                if put_res.status_code != 200:
                    raise Exception(f"Failed to upload file to S3: {put_res.text}")
            
            return asset_id

        logger.info("📤 [SYNC-LABS] Uploading image and audio...")
        image_id = upload_file(image_path)
        audio_id = upload_file(audio_path)
        
        # 2. Trigger LipSync
        payload = {
            "model": "lipsync-1.7.1", # High quality stable model
            "input": [
                {"type": "video", "assetId": image_id}, # API treats static image asset as video input
                {"type": "audio", "assetId": audio_id}
            ],
            "options": {
                "output_format": "mp4",
                "output_fps": 25
            }
        }
        
        gen_res = requests.post(f"{BASE_URL}/generate", headers=HEADERS, json=payload)
        if gen_res.status_code != 201:
            raise Exception(f"Failed to start generation: {gen_res.text}")
        
        video_job_id = gen_res.json()["id"]
        logger.info(f"⏳ [SYNC-LABS] Job {video_job_id} started. Polling...")
        
        # 3. Poll for result
        output_file = f"/app/output/synclabs_{job_id}.mp4"
        max_attempts = 60 # 5 minutes (5s * 60)
        for _ in range(max_attempts):
            status_res = requests.get(f"{BASE_URL}/jobs/{video_job_id}", headers=HEADERS)
            if status_res.status_code == 200:
                job_data = status_res.json()
                status = job_data.get("status")
                
                if status == "COMPLETED":
                    video_url = job_data.get("videoUrl")
                    if not video_url:
                        raise Exception("Job completed but no video URL found")
                    
                    # Download result
                    logger.info(f"📥 [SYNC-LABS] Downloading result from {video_url}")
                    video_content = requests.get(video_url).content
                    with open(output_file, "wb") as f:
                        f.write(video_content)
                    return output_file
                
                elif status == "FAILED":
                    raise Exception(f"Sync Labs job failed: {job_data.get('error')}")
            
            time.sleep(5)
            
        raise Exception("Sync Labs job timed out")
        
    except Exception as e:
        logger.error(f"⚠️ [SYNC-LABS] Error: {e}")
        return None
