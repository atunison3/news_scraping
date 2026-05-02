from datetime import datetime, timedelta
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag

from ..domain.article import Article


CACHE_TTL = timedelta(hours=1)


def extract_date_from_nasa_url(url: str) -> datetime | None:
    parts = urlparse(url).path.strip("/").split("/")

    for i in range(len(parts) - 2):
        year, month, day = parts[i : i + 3]

        if (
            year.isdigit()
            and month.isdigit()
            and day.isdigit()
            and len(year) == 4
            and len(month) == 2
            and len(day) == 2
        ):
            return datetime.fromisoformat(f"{year}-{month}-{day}")

    return None


def extract_nasa_article(article_div: Tag) -> Article | None:
    """Extract article data from a NASA hds-content-item div."""

    heading_link = article_div.select_one("a.hds-content-item-heading")
    title_tag = article_div.select_one(".hds-a11y-heading-22")
    summary_tag = article_div.select_one("p")
    content_type_tag = article_div.select_one(".display-flex span")
    image_tag = article_div.select_one("img")

    if not heading_link or not title_tag:
        return None

    article_url = heading_link.get("href")
    if not article_url:
        return None

    return Article(
        title=title_tag.get_text(strip=True),
        url=article_url,
        source="NASA",
        published_at=extract_date_from_nasa_url(article_url),
        summary=summary_tag.get_text(" ", strip=True) if summary_tag else None,
        content_type=(
            content_type_tag.get_text(strip=True) if content_type_tag else None
        ),
        image_url=image_tag.get("src") if image_tag else None,
    )


def get_nasa_news() -> list[Article]:
    import requests

    url = "https://www.nasa.gov/news/recently-published/"
    headers = {
        "User-Agent": "andy-news-project/1.0 (contact: andrew.e.tunison@gmail.com)",
        "Accept": "text/html,application/xhtml+xml",
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    articles = []

    for article_div in soup.select("div.hds-content-item"):
        article = extract_nasa_article(article_div)

        if article:
            articles.append(article)

    return articles
