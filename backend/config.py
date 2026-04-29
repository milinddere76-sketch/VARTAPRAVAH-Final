import os
from dotenv import load_dotenv
import time

load_dotenv()

# --- REDIS CONFIG ---
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
QUEUE_NAME = "news_queue"

# --- POSTGRES CONFIG ---
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_NAME = os.getenv("DB_NAME", "vartapravah")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")

# --- API KEYS ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
YOUTUBE_STREAM_KEY = os.getenv("YOUTUBE_STREAM_KEY", "")
SYNC_API_KEY = os.getenv("SYNC_API_KEY", "")

# --- PATHS ---
# In our new structure, backend is in /app
# Assets are in /app/assets, Output in /app/output
ASSETS_DIR = os.getenv("ASSETS_DIR", "/app/assets")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/output")
LOG_DIR = os.getenv("LOG_DIR", "/app/logs")

os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# --- TIME HELPER ---
def current_timestamp():
    return int(time.time())

print(f"🚀 [CONFIG] System Paths Initialized:")
print(f"   - Assets: {ASSETS_DIR}")
print(f"   - Output: {OUTPUT_DIR}")
print(f"   - Logs:   {LOG_DIR}")
