import logging
import requests

from datetime import datetime, timedelta
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from ..domain.article import Article

logger = logging.getLogger(__name__)

CACHE_TTL = timedelta(hours=1)

BASE_URL = 'https://investor.textron.com'
NEWS_URL = 'https://investor.textron.com/news-releases/default.aspx'


def extract_textron_article_date(date_text: str) -> datetime | None:
    '''Extract Textron article date.'''

    if not date_text:
        return None

    try:
        return datetime.strptime(date_text.strip(), '%B %d, %Y')
    except ValueError:
        logger.warning('Could not parse Textron article date: %s', date_text)
        return None


def extract_textron_article(article_item: Tag) -> Article | None:
    '''Extract Textron article data from a news item.'''

    link_tag = article_item.select_one('.evergreen-news-headline-link')
    date_tag = article_item.select_one('.evergreen-news-date')

    if link_tag is None:
        return None

    href = link_tag.get('href')
    title = link_tag.get_text(' ', strip=True)

    if not href or not title:
        return None

    article_url = urljoin(BASE_URL, href)

    date_text = date_tag.get_text(' ', strip=True) if date_tag else None

    return Article(
        url=article_url,
        title=title,
        source='Textron',
        published_at=extract_textron_article_date(date_text) if date_text else None,
    )


def get_textron_news() -> list[Article]:
    '''Scrape Textron news releases.'''

    headers = {
        'User-Agent': 'andy-news-project/1.0 (contact: andrew.e.tunison@gmail.com)',
        'Accept': 'text/html,application/xhtml+xml',
    }

    response = requests.get(NEWS_URL, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    print('evergreen-news-item:', len(soup.select('.evergreen-news-item')))
    print('headline links:', len(soup.select('.evergreen-news-headline-link')))
    print('loading text present:', 'Loading...' in response.text)

    article_items = soup.select('#_ctrl0_ctl23_divNewsItemsContainer .evergreen-news-item')

    if not article_items:
        logger.warning('No Textron article items found. Response preview: %s', response.text[:1000])

    articles = []

    for article_item in article_items:
        article = extract_textron_article(article_item)

        if article is not None:
            articles.append(article)

    return articles