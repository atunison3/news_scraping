from datetime import datetime 
from pydantic import BaseModel

class Article(BaseModel):
    id: int | None = None
    url: str 
    title: str 
    source: str 
    published_at: datetime | None = None
    priority: float = 0.5
    language: str | None = None
    has_opened: bool = False
    has_read: bool = False
    thumbs_up: bool | None = None
    summary: str | None = None 
    content_type: str | None = None 
    image_url: str | None = None 
    tags: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __hash__(self):
        return hash(self.url)