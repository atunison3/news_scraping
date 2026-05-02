import sqlite3
from pathlib import Path 
from .scrapers.noaa import get_oceana_news
from .repositories.article_repository import ArticleRepository

DB_PATH = Path('/Users/andrewtunison/app_data/new_articles_dev.db')

def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')

    return conn


def init_db(schema_path: Path):
    '''Initiates the database'''

    with get_connection() as conn:
        with open(schema_path, 'r') as f:
            conn.executescript(f.read())


def scrape_and_insert_articles():
    '''Scrapes articles from NOAA and inserts them into the database'''
    repo = ArticleRepository()
    articles = get_oceana_news()
    for article in articles:
        try:
            repo.create(article)
            print(f"Inserted article: {article.title}")
        except Exception as e:
            print(f"Failed to insert article {article.url}: {e}")


if __name__ == "__main__":
    schema_path = Path(__file__).parent / "schema.sql"
    init_db(schema_path)
    scrape_and_insert_articles()