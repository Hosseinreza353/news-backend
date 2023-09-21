from dataclasses import dataclass
from typing import List


@dataclass
class NewsItem:
    origin: str
    header: str
    abstract: str
    news_url: str
    thumbnail_url: str
    body: str
    keywords: List[str]
