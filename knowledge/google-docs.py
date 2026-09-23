import csv
import io
import logging
import urllib.request
from typing import List, Dict

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KnowledgeBase")

# Public Google Sheet CSV Export Link
SHEET_ID = "1dfqG61RG4HibcZXWVbqu2QigksBkHzUS9GI6dgcGBrI"
GID = "598218105"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

# YouTube Channel Link for Reference Grounding
HANMAK_YOUTUBE_URL = "https://www.youtube.com/results?search_query=hanmak+technologies"


class KnowledgeBaseExtractor:
    """Handles retrieval and matching of troubleshooting articles from Hanmak Knowledge sources."""

    def __init__(self, csv_url: str = CSV_URL):
        self.csv_url = csv_url
        self.articles: List[Dict[str, str]] = []

    def fetch_sheet_data(self) -> List[Dict[str, str]]:
        """Downloads and parses knowledge entries directly from the public Google Sheet CSV."""
        logger.info("Fetching Knowledge Base articles from Google Sheet...")
        try:
            req = urllib.request.Request(self.csv_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as response:
                csv_text = response.read().decode("utf-8")
                reader = csv.DictReader(io.StringIO(csv_text))
                self.articles = [row for row in reader]
                logger.info(f"Successfully loaded {len(self.articles)} knowledge base entries.")
                return self.articles
        except Exception as e:
            logger.error(f"Failed to retrieve Google Sheet data: {e}")
            return []

    def search_knowledge(self, query: str) -> List[Dict[str, str]]:
        """Searches loaded articles for keywords matching support tickets."""
        if not self.articles:
            self.fetch_sheet_data()

        query_words = query.lower().split()
        matched = []

        for article in self.articles:
            # Check content matching against CSV columns
            content = " ".join(article.values()).lower()
            if any(word in content for word in query_words if len(word) > 2):
                matched.append(article)

        return matched

    def get_youtube_reference(self) -> str:
        """Returns official Hanmak Youtube reference link for additional support material."""
        return HANMAK_YOUTUBE_URL


if __name__ == "__main__":
    # Local quick testing
    kb = KnowledgeBaseExtractor()
    kb.fetch_sheet_data()
    print("\n--- Knowledge Base Sample Retrieval ---")
    results = kb.search_knowledge("patient registration")
    print(f"Found {len(results)} matches for 'patient registration'")