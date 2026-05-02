-- Schema for news_scraping database

CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    published_at DATETIME,
    summary TEXT,
    content_type TEXT,
    image_url TEXT,
    has_opened BOOLEAN NOT NULL DEFAULT 0,
    has_read BOOLEAN NOT NULL DEFAULT 0,
    thumbs_up BOOLEAN,
    tags TEXT
);