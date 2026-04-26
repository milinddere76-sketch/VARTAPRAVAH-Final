import redis
import json
import time
import os
from datetime import datetime
from backend import config
from backend.services.news_fetcher import fetch_news
from backend.services.script_generator import generate_script
from backend.services.fact_checker import is_verified
from backend.utils.logger import logger

r = redis.Redis(host=config.REDIS_HOST, port=int(config.REDIS_PORT))

# Keys for rotation
NEWS_ROTATION_KEY = "news_rotation_list"
MAX_NEWS_ITEMS = 25

def get_next_anchor():
    anchor = r.get("anchor_toggle") or b"female"
    next_anchor = "male" if anchor == b"female" else "female"
    r.set("anchor_toggle", next_anchor)
    return anchor.decode()

def update_rotation(new_articles):
    """Maintains the latest 25 news items in rotation."""
    for article in new_articles:
        # Push to the left (newest)
        r.lpush(NEWS_ROTATION_KEY, article)
    
    # Trim to keep only the latest 25
    r.ltrim(NEWS_ROTATION_KEY, 0, MAX_NEWS_ITEMS - 1)
    
    # Get current rotation
    items = r.lrange(NEWS_ROTATION_KEY, 0, -1)
    return [i.decode() for i in items]

def get_bulletin_type():
    hour = datetime.now().hour
    if 5 <= hour < 10: return "सकाळ"
    elif 10 <= hour < 14: return "दुपार"
    elif 14 <= hour < 18: return "संध्याकाळ"
    elif 18 <= hour < 22: return "प्राइम टाइम"
    else: return "रात्री"

def main():
    logger.info("🏢 [TV-LOGIC] Master Scheduler with News Rotation Active.")

    while True:
        try:
            bulletin_type = get_bulletin_type()
            logger.info(f"🕒 Slot: {bulletin_type}")
            
            # 1. Fetch fresh news
            raw_articles = fetch_news()
            verified_new = []

            for art in raw_articles:
                if isinstance(art, str) and art.startswith("---"): continue # Skip headers
                if is_verified(art):
                    verified_new.append(art)

            # 2. Update rotation and get current 25
            rotation = update_rotation(verified_new)
            
            if len(rotation) < 5:
                logger.warning(f"⚠️ Only {len(rotation)} news items available. Minimum 5 required.")
                time.sleep(300)
                continue

            # 3. Handle Breaking News (if more than 25 new items arrived, but update_rotation already trims)
            # If we want a special flag:
            is_breaking = len(verified_new) > 10 # Example threshold
            
            # 4. Generate Script
            anchor_type = get_next_anchor()
            prompt_context = "\n".join(rotation)
            
            logger.info(f"✍️ Generating {bulletin_type} script for {len(rotation)} items...")
            script = generate_script(prompt_context)

            if script:
                r.rpush(config.QUEUE_NAME, json.dumps({
                    "id": int(time.time()),
                    "type": bulletin_type,
                    "is_breaking": is_breaking,
                    "anchor_type": anchor_type,
                    "script": script,
                    "headlines": rotation # Pass headlines for the ticker/flash
                }))
                logger.info(f"✅ Bulletin queued with {len(rotation)} items.")

            # 30-minute cycle
            time.sleep(1800)

        except Exception as e:
            logger.error(f"Scheduler Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
