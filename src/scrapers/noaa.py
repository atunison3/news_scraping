import requests
from datetime import datetime, timedelta
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from ..domain.article import Article


CACHE_TTL = timedelta(hours=1)


def extract_article_title(url: str) -> str:
    '''Extracts NOAA article title'''

    title = ' '.join(url.split('/')[-2].split('-')).title()

    return title

def extract_article_date(date: str) -> datetime:
    '''Extracts the NOAA article date'''

    date = datetime.fromisoformat(date[:10])

    return date


def get_oceana_news() -> list[Article]:

    url = 'https://oceana.org/press-releases-sitemap2.xml'
    headers = {
        'User-Agent': 'andy-news-project/1.0 (contact: andrew.e.tunison@gmail.com)',
        'Accept': 'text/html,application/xhtml+xml',
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, features='xml')

    articles = []

    for url_tag in soup.find_all('url'):
        loc = url_tag.find('loc')
        lastmod = url_tag.find('lastmod')

        if loc is None:
            continue

        article_url = loc.get_text(strip=True)

        if not article_url.startswith('https://oceana.org/press-releases/'):
            continue

        date_text = lastmod.get_text(strip=True) if lastmod else None

        articles.append(
            Article(
                url=article_url,
                title=extract_article_title(article_url),
                source='Oceana',
                published_at=extract_article_date(date_text) if date_text else None,
            )
        )

    return articles