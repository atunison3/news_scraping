import logging
import requests

from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from models.article import Article

logger = logging.getLogger(__name__)


def extract_ncaa_article(row: Tag) -> Article | None:
    '''Extract article data from an NCAA archive table row.'''

    link = row.select_one('td a[href]')

    if link is None:
        return None

    article_path = link.get('href')

    if not article_path:
        return None

    title = link.get_text(' ', strip=True)
    article_url = urljoin('https://www.ncaa.org', article_path)

    summary_tag = row.select_one('.sidearm-archives-summary')
    summary = (
        summary_tag.get_text(' ', strip=True)
        if summary_tag is not None
        else None
    )

    cells = row.select('td')
    published_at = None

    if cells:
        raw_date = cells[-1].get_text(strip=True)

        try:
            published_at = datetime.strptime(raw_date, '%m/%d/%Y')
        except ValueError:
            published_at = None

    return Article(
        title=title,
        url=article_url,
        source='NCAA',
        published_at=published_at,
        summary=summary,
        read_time=None,
        content_type=None,
        image_url=None,
    )


def get_ncaa_news() -> list[Article]:
    '''Fetch NCAA media center articles from the archive page.'''

    archive_url = 'https://www.ncaa.org/archives?path=media-center'

    headers = {
        'User-Agent': 'andy-news-project/1.0 (contact: andrew.e.tunison@gmail.com)',
        'Accept': 'text/html,application/xhtml+xml',
    }

    response = requests.get(archive_url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    print('tr:', len(soup.select('tr')))
    print('archives:', len(soup.select('.sidearm-archives')))
    print('links:', len(soup.select('a[href]')))

    for link in soup.select('a[href]')[:20]:
        print(link.get_text(' ', strip=True), link.get('href'))

    articles = []

    logger.info('Returned %s articles from NCAA', len(articles))

    return articles