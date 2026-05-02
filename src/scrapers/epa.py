# src/scrapers/epa.py

from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from ..domain.article import Article

EPA_NEWS_URL = "https://www.epa.gov/newsreleases"


def parse_epa_date(date_text: str | None) -> str | None:
    if not date_text:
        return None

    return datetime.strptime(date_text.strip(), "%B %d, %Y").date().isoformat()


def get_epa_news() -> list[Article]:
    response = requests.get(
        EPA_NEWS_URL,
        headers={
            "User-Agent": "news-app/0.1 personal learning project",
        },
        timeout=10,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    articles = []

    for item in soup.select("li.usa-collection__item"):
        link = item.select_one("h3.usa-collection__heading a.usa-link")

        if link is None:
            continue

        title = link.get_text(strip=True)
        url = urljoin(EPA_NEWS_URL, link.get("href", ""))

        descriptions = [
            p.get_text(" ", strip=True)
            for p in item.select("p.usa-collection__description")
            if p.get_text(strip=True)
        ]

        summary = descriptions[-1] if descriptions else None

        time_tag = item.select_one("time[datetime]")
        published_at = None

        if time_tag:
            published_at = time_tag.get("datetime")
        else:
            date_node = item.select_one("li.usa-collection__meta-item time")
            published_at = parse_epa_date(
                date_node.get_text(strip=True) if date_node else None
            )

        articles.append(
            Article(
                url=url,
                title=title,
                source="EPA",
                published_at=published_at,
                summary=summary,
            )
        )

    return articles
