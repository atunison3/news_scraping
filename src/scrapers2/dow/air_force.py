from datetime import datetime, timedelta

import requests

from bs4 import BeautifulSoup, Tag

from models.article import Article


CACHE_TTL = timedelta(hours=1)

AIR_FORCE_NEWS_URL = 'https://www.af.mil/News/'


def parse_air_force_date(raw_date: str | None) -> datetime | None:
    if not raw_date:
        return None

    try:
        return datetime.fromisoformat(raw_date)
    except ValueError:
        return None


def extract_air_force_article(article_tag: Tag) -> Article | None:
    link_tag = article_tag.select_one('.summary h1 a[href]')
    time_tag = article_tag.select_one('.summary time[datetime]')
    summary_tag = article_tag.select_one('.summary p')
    image_tag = article_tag.select_one('.thumb img')

    if not link_tag:
        return None

    article_url = link_tag.get('href')
    title = link_tag.get_text(' ', strip=True)

    if not article_url or not title:
        return None

    return Article(
        title=title,
        url=article_url,
        source='Air Force',
        published_at=(
            parse_air_force_date(time_tag.get('datetime'))
            if time_tag
            else None
        ),
        read_time=None,
        summary=(
            summary_tag.get_text(' ', strip=True)
            if summary_tag
            else None
        ),
        content_type='News',
        image_url=image_tag.get('src') if image_tag else None,
    )


def get_air_force_news() -> list[Article]:
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/124.0.0.0 Safari/537.36'
        ),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'https://www.af.mil/',
    }

    with requests.Session() as session:
        session.headers.update(headers)

        response = session.get('https://www.af.mil/', timeout=20)
        response.raise_for_status()

        response = session.get('https://www.af.mil/News/', timeout=20)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []

    for article_tag in soup.select('ul.article-listing-news article.article-listing-item'):
        article = extract_air_force_article(article_tag)

        if article:
            articles.append(article)

    return articles