import os
from backend import config
from backend.utils.logger import logger

# Lazy import for Coqui TTS to prevent initialization errors if not needed
tts_instance = None

def init_tts():
    """Initializes the Neural XTTS v2 engine with error resilience."""
    global tts_instance
    try:
        from TTS.api import TTS
        model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        logger.info(f"🎙️ [TTS] Initializing Neural XTTS v2 ({model_name})...")
        
        # Check for GPU
        device = "cuda" if os.getenv("USE_GPU") == "True" else "cpu"
        tts_instance = TTS(model_name=model_name).to(device)
        logger.info(f"✅ [TTS] Engine initialized on {device}")
    except Exception as e:
        logger.error(f"❌ [TTS] Coqui initialization failed: {e}")
        tts_instance = "FAILED"

def generate_audio(text, file_path):
    """
    Generates Marathi audio. 
    1. Primary: Neural Coqui XTTS v2 for clear, energetic TV-style.
    2. Fallback: gTTS for zero-downtime reliability.
    """
    global tts_instance
    
    if not text or str(text).strip() == "":
        logger.warning("⚠️ [TTS] Received empty text. Using default fallback message.")
        text = "नमस्कार, वार्ता प्रवाह मधे आपले स्वागत आहे. सध्या कोणतीही नवीन बातमी उपलब्ध नाही."

    if tts_instance is None:
        init_tts()

    # --- PRIMARY: COQUI XTTS v2 ---
    if tts_instance and tts_instance != "FAILED":
        try:
            # We use a high-energy Marathi anchor sample for zero-shot cloning
            anchor_sample = os.path.join(config.ASSETS_DIR, "anchor_voice.wav")
            
            # Use fallback sample if preferred one is missing
            if not os.path.exists(anchor_sample):
                anchor_sample = None # Coqui will use default speaker
            
            logger.info(f"🎙️ [TTS] Synthesizing Neural Marathi voice...")
            tts_instance.tts_to_file(
                text=text,
                language="mr",
                speaker_wav=anchor_sample,
                file_path=file_path,
                speed=1.1 # Slightly faster for 'energetic' TV tone
            )
            
            if os.path.exists(file_path):
                return file_path
        except Exception as e:
            logger.warning(f"⚠️ [TTS] Neural synthesis failed, triggering gTTS fallback: {e}")

    # --- FALLBACK: gTTS ---
    import time
    for attempt in range(3):
        try:
            logger.info(f"🛡️ [TTS] Using gTTS Fallback for Marathi audio (Attempt {attempt+1})...")
            from gtts import gTTS
            tts_fallback = gTTS(text=text, lang='mr', slow=False)
            tts_fallback.save(file_path)
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                return file_path
        except Exception as e:
            if "429" in str(e):
                wait_time = (attempt + 1) * 2
                logger.warning(f"⚠️ [TTS] gTTS Rate Limited (429). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"❌ [TTS] gTTS Error: {e}")
                break

    # Final emergency fallback: Use anchor_voice.wav as a placeholder if nothing else works
    emergency_sample = os.path.join(config.ASSETS_DIR, "anchor_voice.wav")
    if os.path.exists(emergency_sample):
        import shutil
        shutil.copy(emergency_sample, file_path)
        logger.warning(f"🚨 [TTS] TOTAL FAILURE. Using emergency voice sample for {file_path}")
        return file_path

    return None

class TTSEngine:
    def generate_audio(self, text, output_path):
        return generate_audio(text, output_path)
