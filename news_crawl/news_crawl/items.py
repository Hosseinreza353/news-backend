from dataclasses import dataclass
from typing import List


@dataclass
class NewsItem:
    publisher: str
    header: str
    abstract: str
    news_url: str
    thumbnail_url: str
    body: str
    category: str
    time: str
    keywords: List[str]
