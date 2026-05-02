import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta

from models.article import Article  # adjust import path

CACHE_TTL = timedelta(hours=1)


def get_white_house_news() -> list[Article]:
    """Queries the news on whitehouse.gov and returns Article objects"""

    url = "https://www.whitehouse.gov/news/"
    headers = {
        "User-Agent": "andy-data-project/1.0 (contact: andrew.e.tunison@gmail.com)",
        "Accept": "text/html,application/xhtml+xml",
    }

    html = requests.get(url, headers=headers, timeout=20).text
    soup = BeautifulSoup(html, "html.parser")

    results: list[Article] = []

    for h2 in soup.select("h2:has(a)"):
        a = h2.find("a")
        if not a:
            continue

        # safer: climb to nearest <li> (actual article container)
        container = h2.find_parent("li")
        if not container:
            continue

        time_tag = container.find("time")
        if not time_tag:
            continue

        try:
            article_date = datetime.fromisoformat(time_tag["datetime"]).astimezone(
                timezone.utc
            )
        except Exception:
            continue

        # filter: last 7 days
        now = datetime.now(timezone.utc)
        if (now - article_date).days > 7:
            continue

        try:
            article = Article(
                title=a.get_text(strip=True),
                url=a["href"],
                source="White House",
                published_at=article_date,
            )
            results.append(article)

        except Exception:
            # skip malformed entries
            continue

    return results
