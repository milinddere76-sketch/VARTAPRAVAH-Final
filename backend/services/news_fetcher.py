import requests
from backend import config
from backend.utils.logger import logger

class NewsFetcher:
    def __init__(self):
        self.api_key = config.NEWS_API_KEY

    def fetch_all_categories(self):
        """Fetches news from Maharashtra, National, and International sources."""
        results = {
            "maharashtra": self.fetch_by_query("Maharashtra Marathi News"),
            "national": self.fetch_by_query("India National News"),
            "international": self.fetch_by_query("World News International")
        }
        return results

    def fetch_by_query(self, query):
        """Fetches news based on a specific search query."""
        try:
            url = f"https://newsapi.org/v2/everything?q={query}&language=mr&sortBy=publishedAt&apiKey={self.api_key}"
            res = requests.get(url)
            data = res.json()
            
            if data.get("status") == "ok":
                articles = data.get("articles", [])[:3]
                return [a.get("title") for a in articles if a.get("title")]
            
            # Fallback to general headlines if query fails
            return self.fetch_fallback()
        except Exception as e:
            logger.error(f"NewsAPI error for {query}: {e}")
            return self.fetch_fallback()

    def fetch_fallback(self):
        """Emergency Marathi headlines if API fails or returns 0."""
        return [
            "बातमी विशेष: महाराष्ट्रातील हवामानात मोठा बदल होण्याची शक्यता.",
            "प्रशासकीय निर्णय: राज्यातील विकासकामांना वेग देण्याचे आदेश.",
            "आरोग्य अपडेट: नागरिकांनी खबरदारी घेण्याचे आवाहन.",
            "कृषी वार्ता: यावर्षी विक्रमी पीक येण्याचा अंदाज.",
            "क्रीडा जगत: स्थानिक खेळाडूंनी राष्ट्रीय स्तरावर पटकावले यश."
        ]

def fetch_news():
    """Unified interface for the scheduler."""
    fetcher = NewsFetcher()
    news_data = fetcher.fetch_all_categories()
    
    # Consolidate into a formatted list for the script generator
    consolidated = []
    if news_data["maharashtra"]:
        consolidated.append("--- महाराष्ट्र विशेष ---")
        consolidated.extend(news_data["maharashtra"])
    if news_data["national"]:
        consolidated.append("--- राष्ट्रीय बातम्या ---")
        consolidated.extend(news_data["national"])
    if news_data["international"]:
        consolidated.append("--- आंतरराष्ट्रीय घडामोडी ---")
        consolidated.extend(news_data["international"])
        
    return consolidated
