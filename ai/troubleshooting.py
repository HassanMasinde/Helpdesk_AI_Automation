"""
ai/troubleshooting.py

Loads the Sheet2 troubleshooting library (technical issues + fixes) from the
same public Google Sheet used for the How-To knowledge base.

Sheet2 columns:
  Section / Category
  Issue / Problem Title
  Layman Description / Problem Details
  Technical Jargon / Root Cause
  Resolution Steps / Fix Explanation
"""

import csv
import io
import logging
import urllib.request

logger = logging.getLogger("Troubleshooting")

SHEET_ID = "1dfqG61RG4HibcZXWVbqu2QigksBkHzUS9GI6dgcGBrI"
TROUBLESHOOTING_GID = "123456"
CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export"
    f"?format=csv&gid={TROUBLESHOOTING_GID}"
)

FIELDS = (
    "Section / Category",
    "Issue / Problem Title",
    "Layman Description / Problem Details",
    "Technical Jargon / Root Cause",
    "Resolution Steps / Fix Explanation",
)


class TroubleshootingBase:
    """Fetches and searches Sheet2 troubleshooting articles."""

    def __init__(self, csv_url: str = CSV_URL):
        self.csv_url = csv_url
        self.articles = []

    def fetch(self):
        logger.info("Fetching troubleshooting articles from Sheet2...")
        try:
            req = urllib.request.Request(self.csv_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as response:
                text = response.read().decode("utf-8", "replace")
        except Exception as error:  # noqa: BLE001 - never crash the agent on fetch
            logger.error(f"Failed to retrieve Sheet2 troubleshooting data: {error}")
            self.articles = []
            return []

        lines = text.splitlines()
        header_index = None
        for index, line in enumerate(lines):
            if "Section / Category" in line and "Issue / Problem Title" in line:
                header_index = index
                break

        if header_index is None:
            logger.error("Sheet2 header row not found.")
            self.articles = []
            return []

        reader = csv.DictReader(io.StringIO("\n".join(lines[header_index:])))
        articles = []
        for row in reader:
            if any((row.get(field) or "").strip() for field in FIELDS):
                articles.append(row)

        self.articles = articles
        logger.info(f"Loaded {len(self.articles)} troubleshooting entries from Sheet2.")
        return self.articles

    def search(self, query: str):
        if not self.articles:
            self.fetch()

        words = [word for word in (query or "").lower().split() if len(word) > 2]
        if not words:
            return []

        scored = []
        for article in self.articles:
            content = " ".join((article.get(field) or "") for field in FIELDS).lower()
            score = sum(1 for word in words if word in content)
            if score:
                scored.append((score, article))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [article for _, article in scored[:5]]
