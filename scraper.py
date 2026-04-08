import re
import requests
from bs4 import BeautifulSoup

from messages import ERROR_SCRAPING

CNBC_REAL_ESTATE_URL = "https://www.cnbc.com/real-estate/"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
MAX_ARTICLES = 5
_ARTICLE_PATTERN = re.compile(r"https://www\.cnbc\.com/\d{4}/\d{2}/\d{2}/.+\.html")


def scrape_cnbc_real_estate(max_articles=MAX_ARTICLES):
    try:
        response = requests.get(CNBC_REAL_ESTATE_URL, headers=_HEADERS, timeout=10)
        response.raise_for_status()
    except Exception as e:
        raise RuntimeError(ERROR_SCRAPING) from e

    soup = BeautifulSoup(response.text, "html.parser")

    seen = set()
    urls = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not href.startswith("http"):
            href = "https://www.cnbc.com" + href
        if _ARTICLE_PATTERN.match(href) and href not in seen:
            seen.add(href)
            urls.append(href)
            if len(urls) >= max_articles:
                break

    return urls
