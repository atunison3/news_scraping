from typing import List, Optional
from ..domain.article import Article
from ..repositories.article_repository import ArticleRepository

class ArticleService:
    def __init__(self, repository: ArticleRepository):
        self.repository = repository

    def create_article(self, article: Article) -> Article:
        # Business logic: ensure URL is unique, validate data, etc.
        if not article.url or not article.title or not article.source:
            raise ValueError("Article must have url, title, and source")
        # Check if article with same URL already exists
        existing = self.repository.get_all()
        if any(a.url == article.url for a in existing):
            raise ValueError("Article with this URL already exists")
        return self.repository.create(article)

    def get_article_by_id(self, article_id: int) -> Optional[Article]:
        return self.repository.get_by_id(article_id)

    def get_all_articles(self) -> List[Article]:
        return self.repository.get_all()

    def update_article(self, article: Article) -> bool:
        if not article.id:
            raise ValueError("Article must have an ID to update")
        return self.repository.update(article)