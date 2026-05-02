import re

from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup, Tag

from ..domain.article import Article


CACHE_TTL = timedelta(hours=1)

BASE_URL = 'https://about.fb.com'
NEWS_URL = 'https://about.fb.com/news/'


def parse_meta_date(text: str) -> datetime | None:
    date_pattern = r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}'
    match = re.search(date_pattern, text)

    if not match:
        return None

    try:
        return datetime.strptime(match.group(), '%B %d, %Y')
    except ValueError:
        return None


def is_valid_meta_news_url(url: str) -> bool:
    if not url.startswith('https://about.fb.com/news/'):
        return False

    excluded_parts = [
        '/news/page/',
        '/news/category/',
        '/news/tag/',
        '/news/search/',
    ]

    return not any(part in url for part in excluded_parts)


def clean_text(text: str | None) -> str | None:
    if not text:
        return None

    text = ' '.join(text.split())

    return text or None


def extract_meta_article_from_heading(heading_tag: Tag) -> Article | None:
    link = heading_tag.select_one('a[href*="/news/"]')

    if not link:
        return None

    href = link.get('href')

    if not href:
        return None

    article_url = urljoin(BASE_URL, href)

    if not is_valid_meta_news_url(article_url):
        return None

    title = clean_text(link.get_text(' ', strip=True))

    if not title:
        return None

    card = heading_tag.find_parent()

    card_text = clean_text(card.get_text(' ', strip=True)) if card else None
    published_at = parse_meta_date(card_text or '')

    summary = None

    if card:
        paragraphs = card.select('p')

        for paragraph in paragraphs:
            paragraph_text = clean_text(paragraph.get_text(' ', strip=True))

            if paragraph_text and paragraph_text != title:
                summary = paragraph_text
                break

    image_url = None

    if card:
        image_tag = card.select_one('img')

        if image_tag:
            image_url = image_tag.get('src')

    return Article(
        title=title,
        url=article_url,
        source='Meta',
        published_at=published_at,
        read_time=None,
        summary=summary,
        content_type='News',
        image_url=image_url,
    )


def get_meta_news(max_pages: int = 3) -> list[Article]:
    headers = {
        'User-Agent': 'andy-news-project/1.0 (contact: andrew.e.tunison@gmail.com)',
        'Accept': 'text/html,application/xhtml+xml',
    }

    articles = []
    seen_urls = set()

    for page_number in range(1, max_pages + 1):
        url = NEWS_URL if page_number == 1 else f'{NEWS_URL}page/{page_number}/'

        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        for heading_tag in soup.select('h2, h3'):
            article = extract_meta_article_from_heading(heading_tag)

            if article and article.url not in seen_urls:
                seen_urls.add(article.url)
                articles.append(article)

    return articles