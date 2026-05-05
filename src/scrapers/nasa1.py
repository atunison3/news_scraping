import requests
import time

from bs4 import BeautifulSoup
from datetime import datetime, timezone

from ..domain.article import Article

def extract_nasa_url(element: BeautifulSoup) -> str:
    '''Extracts the actual url string'''

    return element.select('loc')[0].get_text()

def extract_nasa_title(url: str) -> str:
    '''Extracts the NASA title'''

    title = url.replace('https://www.nasa.gov/', '').split('/')[1]
    title = title.replace('-', ' ').title()

    return title

def extract_nasa_tag(url: str) -> str:
    '''Get tags for a NASA article'''

    try:
        tag = url.replace('https://www.nasa.gov/', '').split('/')[0]
    except:
        tag = None

    return tag

def extract_datetime(element: BeautifulSoup) -> datetime:
    '''Extracts the datetime'''

    return datetime.fromisoformat(element.select('lastmod')[0].get_text()).replace(tzinfo=timezone.utc)

def compile_article(element: BeautifulSoup) -> Article:
    '''Compiles into an article'''

    try:
        url = extract_nasa_url(element)
        title = extract_nasa_title(url)
        tag = extract_nasa_tag(url);
        published_at = extract_datetime(element).replace(tzinfo=timezone.utc)
        source = 'NASA'
    
        article = Article(
            url=url,
            title=title,
            tag=tag,
            published_at=published_at,
            source=source
        )
        return article
    except Exception as e:
        pass

    return None


def get_nasa_news() -> list[Article]:    
    # NASA
    url = 'https://www.nasa.gov/wp-sitemap.xml'
    headers = {
        "User-Agent": "andy-news-project/1.0 (contact: andrew.e.tunison@gmail.com)",
        "Accept": "text/html,application/xhtml+xml",
    }    
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "xml")

    sitemaps = [
        sitemap.select_one('loc').get_text()
        for sitemap in soup.select('sitemap')
        if sitemap.select_one('loc').get_text().startswith('https://www.nasa.gov/wp-sitemap-news-')
    ]


    articles = []
    for sitemap in sitemaps:
        time.sleep(1)
        response = requests.get(sitemap, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "xml")    
        for url in soup.select('url'):
            loc = url.select_one('loc').get_text()
            news = url.select_one('news')
            if loc.endswith('/'):
                title = loc[:-1].split('/')[-1].replace('-', ' ').title()
            else:
                title = loc.split('/')[-1].replace('-', ' ').title()
            try:
                language = news.select_one('language').get_text()
            except:
                language = None
            published_at = datetime.fromisoformat(news.select_one('publication_date').get_text()).replace(tzinfo=timezone.utc)
            try:
                tags = news.select_one('keywords').get_text()
            except:
                tags = None
            try:
                priority = float(url.select_one('priority').get_text())
            except Exception as e:
                priority = 0.5
            
            article = Article(
                url=loc,
                title=title,
                tags=tags,
                published_at=published_at,
                source='NASA',
                priority=priority,
                language=language
            )
            articles.append(article)

    return articles