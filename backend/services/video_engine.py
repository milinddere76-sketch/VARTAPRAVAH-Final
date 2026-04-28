import os
from backend import config
from backend.utils.logger import logger

import subprocess

def get_asset_path(filename):
    """Returns the path to an asset, checking the volume first and then internal fallback."""
    paths = [
        os.path.join("/app/assets", filename),
        os.path.join("assets", filename),
        os.path.join("/app/assets_internal", filename)  # Fallback
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return os.path.join("/app/assets", filename)  # Default to volume path

def create_video(sadtalker_video_path, output_path, headlines=None, is_breaking=False):
    logo_path = get_asset_path("varta_logo.png")
    studio_path = get_asset_path("studio.jpg")
    
    # Check for Marathi font in multiple locations
    font_paths = [
        "/usr/share/fonts/truetype/noto/NotoSansMarathi-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansMarathi-UI-Regular.ttf",
        "DejaVu Sans" # Fallback
    ]
    font_path = "DejaVu Sans"
    for p in font_paths:
        if os.path.exists(p):
            font_path = p
            break

    # Preparation - Escape single quotes for FFmpeg drawtext
    def escape_ffmpeg(text):
        if not text: return ""
        return str(text).replace("'", "\\'").replace(":", "\\:")

    if headlines:
        ticker_text = escape_ffmpeg(" | ".join(headlines))
    else:
        ticker_text = "वार्ता प्रवाह - २४/७ बातम्या"

    flash_text = ""
    if headlines and len(headlines) >= 3:
        flash_text = escape_ffmpeg("मुख्य घडामोडी: " + " | ".join(headlines[:3]))

    # --- FFmpeg Filter Construction ---
    filters = "[1:v]scale=1280:720[base];"
    filters += "[0:v]scale=-1:720[anchor];"
    filters += "[base][anchor]overlay=(W-w)/2:H-h[v1];"
    filters += f"[2:v]scale=150:-1[logo];[v1][logo]overlay=W-170:20[v2];"
    
    live_color = "red" if not is_breaking else "orange"
    live_label = escape_ffmpeg("● थेट प्रक्षेपण" if not is_breaking else "● विशेष बातमी")
    
    filters += (
        f"drawtext=text='{live_label}':fontfile='{font_path}':fontcolor=white:fontsize=24:x=30:y=30:"
        f"box=1:boxcolor={live_color}@0.8:boxborderw=10[v3];"
    )
    
    if flash_text:
        filters += (
            f"[v3]drawtext=fontfile='{font_path}':text='{flash_text[:120]}...':x=(w-tw)/2:y=120:"
            f"fontsize=40:fontcolor=yellow:box=1:boxcolor=black@0.6:boxborderw=20:enable='between(t,0,6)'[v4];"
        )
    else:
        filters += "[v3]copy[v4];"
        
    filters += (
        f"[v4]drawtext=fontfile='{font_path}':text='{ticker_text}':x=w-mod(t*220,w+tw):y=h-70:"
        f"fontsize=38:fontcolor=white:box=1:boxcolor=black@0.8:boxborderw=20"
    )

    if not os.path.exists(sadtalker_video_path) or os.path.getsize(sadtalker_video_path) < 1000:
        logger.error(f"❌ [PIPELINE] Invalid input video: {sadtalker_video_path}")
        return None

    cmd = [
        "ffmpeg", "-y",
        "-i", sadtalker_video_path,
        "-i", studio_path,
        "-i", logo_path,
        "-filter_complex", filters,
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        output_path
    ]
    
    logger.info(f"🎬 [PIPELINE] Compositing {output_path}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            logger.error(f"❌ [FFMPEG] Error during composition: {result.stderr}")
            return None
        return output_path
    except Exception as e:
        logger.error(f"❌ [PIPELINE] Unexpected Error during composition: {e}")
        return None

class VideoEngine:
    def generate_video(self, video_path, headlines, output_filename, is_breaking=False):
        output_path = os.path.join(config.OUTPUT_DIR, output_filename)
        return create_video(video_path, output_path, headlines, is_breaking)
