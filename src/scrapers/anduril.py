import requests

from bs4 import BeautifulSoup
from datetime import datetime, timezone

from ..domain.article import Article

    
def get_anduril_news() -> list[Article]:
    # Anduril
    url = 'https://www.anduril.com/sitemap.xml'
    headers = {
        "User-Agent": "andy-news-project/1.0 (contact: andrew.e.tunison@gmail.com)",
        "Accept": "text/html,application/xhtml+xml",
    }    
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "xml")

    # Filter to news articles
    source = 'Anduril'
    urls = [
        url
        for url in soup.select('url')
        if url.select_one('loc') and url.select_one('loc').get_text().startswith('https://www.anduril.com/news/')
    ]

    articles = []
    for url in urls:
        loc = url.select_one('loc').get_text()
        news = url.select_one('news')
        published_at = datetime.fromisoformat(news.select_one('publication_date').get_text()).replace(tzinfo=timezone.utc)
        title = news.select_one('title').get_text()
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
            source=source,
            priority=priority,
            language='en'
        )

        articles.append(article)
    
    return articles
