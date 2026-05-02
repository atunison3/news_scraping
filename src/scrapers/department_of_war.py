import logging
import requests

from bs4 import BeautifulSoup
from datetime import datetime
from ..domain.article import Article

logger = logging.getLogger(__name__)

SITEMAP_INDEX_URL = 'https://www.war.gov/DesktopModules/SiteData/SiteMap.ashx'

HEADERS = {
    "User-Agent": "andy-news-project/1.0 (contact: andrew.e.tunison@gmail.com)",
    "Accept": "text/html,application/xhtml+xml",
}
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/147.0.0.0 Safari/537.36'
    ),
    'Accept': 'application/xml,text/xml,text/html;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.war.gov/',
}


def parse_sitemap_date(value: str | None) -> datetime | None:
    '''Parse a sitemap date into a datetime.'''

    if not value:
        return None

    try:
        return datetime.fromisoformat(value.strip())
    except ValueError:
        return None


def title_from_url(url: str) -> str:
    '''Create a readable title from a Department of War article URL.'''

    slug = url.rstrip('/').split('/')[-1]

    return slug.replace('-', ' ').title()


def get_articlecs_sitemap_urls() -> list[str]:
    '''Return ArticleCS sitemap URLs from the Department of War sitemap index.'''

    try:
        response = requests.get(
            SITEMAP_INDEX_URL,
            headers={
                **HEADERS,
                'Accept': 'application/xml, text/xml, */*;q=0.1',
                'Referer': 'https://www.war.gov/',
            },
            timeout=20,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning('Cannot fetch Department of War sitemap index %s: %s', SITEMAP_INDEX_URL, exc)
        return []

    soup = BeautifulSoup(response.text, 'xml')

    return [
        loc.get_text(strip=True)
        for loc in soup.select('sitemap > loc')
        if '/DesktopModules/ArticleCS/SiteMap.ashx' in loc.get_text(strip=True)
    ]


def extract_articles_from_articlecs_sitemap(sitemap_url: str, since: datetime | None = None) -> list[Article]:
    '''Return articles from one ArticleCS sitemap.'''

    try:
        response = requests.get(
            sitemap_url,
            headers=HEADERS,
            timeout=60,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning('Cannot fetch Department of War secondary sitemap %s: %s', sitemap_url, exc)
        return []

    soup = BeautifulSoup(response.text, 'xml')

    articles: list[Article] = []

    for url_tag in soup.select('url'):
        loc_tag = url_tag.select_one('loc')
        lastmod_tag = url_tag.select_one('lastmod')

        if loc_tag is None:
            continue

        article_url = loc_tag.get_text(strip=True)

        if not article_url:
            continue

        lastmod = None

        if lastmod_tag is not None:
            lastmod = parse_sitemap_date(lastmod_tag.get_text(strip=True))

        if since is not None and (lastmod is None or lastmod <= since):
            continue

        article = Article(
            url=article_url,
            title=title_from_url(article_url),
            source='Department of War',
            published_at=lastmod,
        )

        articles.append(article)

    return articles


def get_war_articles(since: datetime | None = None) -> list[Article]:
    '''Return Department of War articles from ArticleCS sitemap endpoints.

    If `since` is provided, only return articles with a newer published date.
    '''

    sitemap_urls = get_articlecs_sitemap_urls()
    articles_by_url: dict[str, Article] = {}

    for sitemap_url in sitemap_urls:
        try:
            articles = extract_articles_from_articlecs_sitemap(sitemap_url, since)

            for article in articles:
                articles_by_url[article.url] = article

        except requests.RequestException as exc:
            logger.warning(
                'Failed to fetch ArticleCS sitemap %s: %s',
                sitemap_url,
                exc,
            )

    return sorted(
        articles_by_url.values(),
        key=lambda article: article.published_at or datetime.min,
        reverse=True,
    )