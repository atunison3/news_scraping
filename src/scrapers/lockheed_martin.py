import re
import requests

from bs4 import BeautifulSoup
from datetime import datetime, timezone

from ..domain.article import Article


def extract_lm_url(element: BeautifulSoup) -> str:
    '''Extracts the actual url string'''

    return element.select('loc')[0].get_text()
    
def extract_lm_datetime(element: BeautifulSoup) -> datetime:
    '''Extracts the datetime'''

    return datetime.fromisoformat(element.select('lastmod')[0].get_text()).replace(tzinfo=timezone.utc)

def extract_lm_title(url: str) -> datetime:
    '''Extracts the LM title'''

    if len(url) < 56:
        print(url)
    try:
        year = int(url[51:55])
    except KeyError:
        year = 0000
        print(url)
    title = f"{year} - {url[56:].replace('--', ': ').replace('-', ' ').title().replace(':', ' -')}"
    title = title.replace('U S', 'US')

    return title

def compile_article(element: BeautifulSoup) -> Article:
    '''Compiles into an article'''

    try:
        url = extract_lm_url(element)
        title = extract_lm_title(url)
        published_at = extract_lm_datetime(element)
        source = 'Lockheed Martin'
    
        article = Article(
            url=url,
            title=title,
            published_at=published_at,
            source=source
        )
        return article
    except Exception as e:
        pass

    return None

    
def get_lm_news() -> list[Article]:
    # Lockheed martin
    url = 'https://www.lockheedmartin.com/sitemap-en-us.xml'
    headers = {
        "User-Agent": "andy-news-project/1.0 (contact: andrew.e.tunison@gmail.com)",
        "Accept": "text/html,application/xhtml+xml",
    }    
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "xml")

    pattern = re.compile(r'(?:^|/)(19|20)\d{2}/')

    elements = soup.select('url')
    articles = []
    for element in elements:
        url = element.select('loc')[0].get_text()
        if ('us/news/features' in url) and pattern.search(url):
            articles.append(compile_article(element))
    
    return articles