import logging
import sqlite3
from pathlib import Path
from .scrapers.epa import get_epa_news
from .scrapers.meta import get_meta_news
from .scrapers.nasa1 import get_nasa_news
from .scrapers.noaa import get_oceana_news
from .scrapers.department_of_war import get_war_articles
from .scrapers.white_house import get_white_house_news
from .scrapers.lockheed_martin import get_lm_news
from .scrapers.anduril import get_anduril_news
from .repositories.article_repository import ArticleRepository

DB_PATH = Path('/Users/andrewtunison/app_data/new_articles_dev.db')
LOG_PATH = Path('/Users/andrewtunison/app_logs/news_scraping_dev.log')
logger = logging.getLogger('news_scraping')


def configure_logging():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler = logging.FileHandler(LOG_PATH, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    else:
        logger.handlers = [file_handler, console_handler]


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
        cursor = conn.cursor()
        cursor.execute('PRAGMA table_info(articles)')
        columns = [row['name'] for row in cursor.fetchall()]
        if 'has_opened' not in columns:
            if 'has_read' in columns:
                cursor.execute('ALTER TABLE articles RENAME COLUMN has_read TO has_opened')
            else:
                cursor.execute('ALTER TABLE articles ADD COLUMN has_opened BOOLEAN NOT NULL DEFAULT 0')
        if 'has_read' not in columns:
            cursor.execute('ALTER TABLE articles ADD COLUMN has_read BOOLEAN NOT NULL DEFAULT 0')
        if 'thumbs_up' not in columns:
            cursor.execute('ALTER TABLE articles ADD COLUMN thumbs_up BOOLEAN')


def scrape_and_insert_articles():
    '''Scrapes articles from configured sources and inserts them into the database.'''
    repo = ArticleRepository()

    def insert_new_articles(source: str, fetcher, *args):
        try:
            articles = fetcher(*args)
        except Exception as exc:
            logger.warning('Skipping %s because the scraper failed: %s', source, exc)
            return 0
        last_article = repo.get_last_article_by_source(source)
        last_published = last_article.published_at if last_article else None
        new_articles = [
            article for article in articles
            if article.published_at and (last_published is None or article.published_at > last_published)
        ]
        new_articles.sort(key=lambda article: article.published_at)

        if not new_articles:
            logger.info('No new %s articles to insert.', source)
            return 0

        inserted = 0
        for article in new_articles:
            try:
                repo.create(article)
                inserted += 1
            except Exception as e:
                logger.error('Failed to insert article %s: %s', article.url, e)

        logger.info('Inserted %d new %s articles.', inserted, source)
        return inserted

    insert_new_articles('Anduril', get_anduril_news)
    insert_new_articles('Oceana', get_oceana_news)
    insert_new_articles('Meta', get_meta_news)
    # insert_new_articles('NASA', get_nasa_news)
    insert_new_articles('White House', get_white_house_news)
    insert_new_articles('EPA', get_epa_news)
    last_war_article = repo.get_last_article_by_source('Department of War')
    last_war_published = last_war_article.published_at if last_war_article else None
    insert_new_articles('Department of War', get_war_articles, last_war_published)
    insert_new_articles('Lockheed Martin', get_lm_news)
    # insert_new_articles('Textron', get_textron_news)  # TODO: Textron uses JS to fill the articles


if __name__ == "__main__":
    configure_logging()
    schema_path = Path(__file__).parent / "schema.sql"
    init_db(schema_path)
    scrape_and_insert_articles()