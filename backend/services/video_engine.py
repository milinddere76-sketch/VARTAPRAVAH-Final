import os
from .. import config
from ..utils.logger import logger

def create_video(sadtalker_video_path, output_path, headlines=None, is_breaking=False):
    """
    Advanced Video Pipeline using FFmpeg:
    1. Background: Studio Virtual Set (studio.jpg)
    2. Overlay: AI Anchor with alpha/chromakey or scaled overlay
    3. Overlays: Channel Logo, LIVE/BREAKING Badge
    4. Lower Thirds: News Ticker and Flash Headlines
    """
    logo_path = os.path.join(config.ASSETS_DIR, "varta_logo.png")
    studio_path = os.path.join(config.ASSETS_DIR, "studio.jpg")
    font_path = "/usr/share/fonts/truetype/noto/NotoSansMarathi-Regular.ttf"
    
    if not os.path.exists(font_path):
        font_path = "DejaVu Sans"

    # Preparation
    if headlines:
        ticker_text = " | ".join(headlines).replace("'", "").replace("\"", "")
    else:
        ticker_text = "वार्ता प्रवाह - २४/७ बातम्या"

    flash_text = ""
    if headlines and len(headlines) >= 3:
        flash_text = "मुख्य घडामोडी: " + " | ".join(headlines[:3])

    # --- FFmpeg Filter Construction ---
    # [0:v] Anchor Video
    # [1:v] Studio Background
    # [2:v] Logo
    
    # 1. Start with Studio Background (1280x720)
    filters = "[1:v]scale=1280:720[base];"
    
    # 2. Scale and Position Anchor (Side-by-side or Centered)
    # We scale anchor to 800px height and position it on top of the studio
    filters += "[0:v]scale=-1:800[anchor];"
    filters += "[base][anchor]overlay=(W-w)/2:H-h[v1];"
    
    # 3. Add Logo (Top Right)
    filters += f"[2:v]scale=150:-1[logo];[v1][logo]overlay=W-170:20[v2];"
    
    # 4. LIVE / BREAKING Badge (Top Left)
    live_color = "red" if not is_breaking else "orange"
    live_label = "● थेट प्रक्षेपण" if not is_breaking else "● विशेष बातमी"
    filters += (
        f"drawtext=text='{live_label}':fontfile='{font_path}':fontcolor=white:fontsize=24:x=30:y=30:"
        f"box=1:boxcolor={live_color}@0.8:boxborderw=10[v3];"
    )
    
    # 5. Flash Headlines (Animated overlay for first 5s)
    if flash_text:
        # Centered Flash Box
        filters += (
            f"[v3]drawtext=fontfile='{font_path}':text='{flash_text[:120]}...':x=(w-tw)/2:y=120:"
            f"fontsize=40:fontcolor=yellow:box=1:boxcolor=black@0.6:boxborderw=20:enable='between(t,0,6)'[v4];"
        )
    else:
        filters += "[v3]copy[v4];"
        
    # 6. Continuous Scrolling Lower Third Ticker
    # We use a black semi-transparent box for the ticker background
    filters += (
        f"[v4]drawtext=fontfile='{font_path}':text='{ticker_text}':x=w-mod(t*220,w+tw):y=h-70:"
        f"fontsize=38:fontcolor=white:box=1:boxcolor=black@0.8:boxborderw=20"
    )

    # Final Command Assembly
    # Inputs: 0: Anchor, 1: Studio, 2: Logo
    cmd = (
        f'ffmpeg -y -i "{sadtalker_video_path}" -i "{studio_path}" -i "{logo_path}" '
        f'-filter_complex "{filters}" '
        f'-c:v libx264 -preset fast -pix_fmt yuv420p '
        f'-c:a aac -b:a 192k '
        f'"{output_path}"'
    )
    
    logger.info(f"🎬 [PIPELINE] Compositing {output_path}...")
    os.system(cmd)
    return output_path

class VideoEngine:
    def generate_video(self, video_path, headlines, output_filename, is_breaking=False):
        output_path = os.path.join(config.OUTPUT_DIR, output_filename)
        return create_video(video_path, output_path, headlines, is_breaking)
