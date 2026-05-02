import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from ..domain.article import Article

DB_PATH = Path('/Users/andrewtunison/app_data/new_articles_dev.db')

class ArticleRepository:
    def __init__(self):
        self.db_path = DB_PATH

    def _get_connection(self) -> sqlite3.Connection:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        return conn

    def create(self, article: Article) -> Article:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO articles (url, title, source, published_at, summary, content_type, image_url, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article.url,
                article.title,
                article.source,
                article.published_at.isoformat() if article.published_at else None,
                article.summary,
                article.content_type,
                article.image_url,
                article.tags
            ))
            article.id = cursor.lastrowid
            return article

    def get_by_id(self, article_id: int) -> Optional[Article]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
            row = cursor.fetchone()
            if row:
                published_at = datetime.fromisoformat(row['published_at']) if row['published_at'] else None
                return Article(
                    id=row['id'],
                    url=row['url'],
                    title=row['title'],
                    source=row['source'],
                    published_at=published_at,
                    summary=row['summary'],
                    content_type=row['content_type'],
                    image_url=row['image_url'],
                    tags=row['tags']
                )
            return None

    def get_all(self) -> List[Article]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM articles')
            rows = cursor.fetchall()
            return [
                Article(
                    id=row['id'],
                    url=row['url'],
                    title=row['title'],
                    source=row['source'],
                    published_at=datetime.fromisoformat(row['published_at']) if row['published_at'] else None,
                    summary=row['summary'],
                    content_type=row['content_type'],
                    image_url=row['image_url'],
                    tags=row['tags']
                ) for row in rows
            ]

    def get_last_article_by_source(self, source: str) -> Optional[Article]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT * FROM articles
                WHERE source = ? AND published_at IS NOT NULL
                ORDER BY published_at DESC, id DESC
                LIMIT 1
                ''',
                (source,)
            )
            row = cursor.fetchone()
            if row:
                published_at = datetime.fromisoformat(row['published_at']) if row['published_at'] else None
                return Article(
                    id=row['id'],
                    url=row['url'],
                    title=row['title'],
                    source=row['source'],
                    published_at=published_at,
                    summary=row['summary'],
                    content_type=row['content_type'],
                    image_url=row['image_url'],
                    tags=row['tags']
                )
            return None

    def update(self, article: Article) -> bool:
        if article.id is None:
            return False
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE articles SET
                    url = ?, title = ?, source = ?, published_at = ?, summary = ?,
                    content_type = ?, image_url = ?, tags = ?
                WHERE id = ?
            ''', (
                article.url,
                article.title,
                article.source,
                article.published_at.isoformat() if article.published_at else None,
                article.summary,
                article.content_type,
                article.image_url,
                article.tags,
                article.id
            ))
            return cursor.rowcount > 0

    def delete(self, article_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM articles WHERE id = ?', (article_id,))
            return cursor.rowcount > 0