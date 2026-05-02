from datetime import datetime 
from pydantic import BaseModel

class Article(BaseModel):
    id: int | None
    url: str 
    title: str 
    source: str 
    published_at: datetime | None
    summary: str | None
    content_type: str | None 
    image_url: str | None 
    tags: str | None