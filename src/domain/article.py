from datetime import datetime 
from pydantic import BaseModel

class Article(BaseModel):
    id: int | None = None
    url: str 
    title: str 
    source: str 
    published_at: datetime | None = None
    summary: str | None = None 
    content_type: str | None = None 
    image_url: str | None = None 
    tags: str | None = None