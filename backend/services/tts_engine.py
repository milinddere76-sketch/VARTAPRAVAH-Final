import os
import time
import logging

logger = logging.getLogger("tts_engine")

# =========================
# CONFIG
# =========================
OUTPUT_DIR = "/tmp/tts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

USE_COQUI = True   # PRIMARY ENGINE
USE_GTTS = True    # FALLBACK

MAX_RETRIES = 3

# =========================
# LOAD COQUI MODEL (ONCE)
# =========================
tts_model = None

def init_tts():
    global tts_model
    if USE_COQUI:
        try:
            from TTS.api import TTS
            logger.info("🔊 Loading Coqui XTTS v2 model...")
            tts_model = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
            logger.info("✅ Coqui TTS loaded successfully")
        except Exception as e:
            logger.error(f"❌ Coqui load failed: {e}")
            tts_model = None

# =========================
# MAIN FUNCTION
# =========================
def generate_audio(text: str, output_path: str = None, voice="female"):
    """
    Returns: audio file path OR None
    """

    if not text or not text.strip():
        logger.error("❌ Empty text received for TTS")
        return None

    if not output_path:
        filename = f"{int(time.time())}.wav"
        output_path = os.path.join(OUTPUT_DIR, filename)

    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"🎙️ TTS Attempt {attempt+1}")

            # =========================
            # PRIMARY: COQUI XTTS
            # =========================
            if USE_COQUI and tts_model:
                tts_model.tts_to_file(
                    text=text,
                    file_path=output_path,
                    language="hi"  # Marathi works via Hindi phonetics
                )

            # =========================
            # FALLBACK: gTTS
            # =========================
            elif USE_GTTS:
                from gtts import gTTS
                tts = gTTS(text=text, lang="hi")
                tts.save(output_path)

            else:
                raise Exception("No TTS engine available")

            # =========================
            # VALIDATION
            # =========================
            if not os.path.exists(output_path):
                raise Exception("Audio file not created")

            if os.path.getsize(output_path) < 1000:
                raise Exception("Audio file too small (corrupt)")

            logger.info(f"✅ TTS SUCCESS: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"❌ TTS Attempt {attempt+1} failed: {e}")
            time.sleep(2)

    logger.error("🚨 ALL TTS ATTEMPTS FAILED")
    return None