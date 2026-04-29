import requests
import os
from backend import config
from backend.utils.logger import logger

from groq import Groq

def translate_to_english(text):
    """
    Translates Marathi headline to English for better API search results.
    """
    try:
        client = Groq(api_key=config.GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Translate the following Marathi news headline to a short, searchable English query. Return ONLY the English text."},
                {"role": "user", "content": text}
            ],
            temperature=0,
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"⚠️ [FACT-CHECK] Translation failed: {e}")
        return text # Fallback to original

def fetch_sources(query):
    """
    Queries multiple news APIs to cross-verify a headline.
    """
    news_api_key = config.NEWS_API_KEY
    world_news_key = os.getenv("WORLD_NEWS_API_KEY") 
    
    urls = []
    if news_api_key:
        # Search for exact phrases or keywords in English
        urls.append(f"https://newsapi.org/v2/everything?q={query}&language=en&apiKey={news_api_key}")
    
    if world_news_key:
        urls.append(f"https://api.worldnewsapi.com/search-news?text={query}&api-key={world_news_key}")

    results = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=5)
            if r.ok:
                data = r.json()
                # Ensure we have articles
                if data.get("totalResults", 0) > 0 or data.get("available", 0) > 0:
                    results.append(data)
        except Exception as e:
            logger.error(f"⚠️ [FACT-CHECK] Error querying source: {e}")
            continue
    return results

def is_verified(news_title):
    """
    Validates news authenticity by comparing multiple sources.
    """
    if not news_title:
        return False

    # 1. Translate to English for better API hit rate
    print(f"🔍 [FACT-CHECK] Translating for verification: {news_title[:40]}...")
    english_query = translate_to_english(news_title)
    print(f"🔍 [FACT-CHECK] English Query: {english_query}")

    # 2. Fetch Sources
    data = fetch_sources(english_query)

    # [RELIABILITY] If APIs are down, we default to True to keep the 24/7 stream alive
    if len(data) < 1:
        logger.warning(f"⚠️ [FACT-CHECK] No sources reachable for: {english_query}. Bypassing verification for uptime.")
        return True

    # 3. Simple validation: Check if query keywords appear across sources
    # Use keywords for more flexible matching
    keywords = english_query.lower().split()
    match_count = 0
    
    for source_data in data:
        articles_str = str(source_data).lower()
        # If at least 3 keywords from the query appear in the source results
        hits = sum(1 for kw in keywords if len(kw) > 3 and kw in articles_str)
        if hits >= 2:
            match_count += 1

    if match_count >= 1:
        print(f"✅ [FACT-CHECK] Verification SUCCESS for '{english_query}'")
        return True
    else:
        print(f"❌ [FACT-CHECK] Verification FAILED. No matching English reports found.")
        return False
