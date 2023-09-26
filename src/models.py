import uuid
from pydantic import BaseModel, Field
from typing import Optional, List


class NewsBase(BaseModel):
    publisher: str = Field(...)
    header: str = Field(...)
    abstract: str = Field(...)
    news_url: str = Field(...)
    thumbnail_url: str = Field(...)
    body: str = Field(...)
    category: str = Field(...)
    keywords: List[str] = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "publisher": "IRNA",
                "header": "Real state prices skyrocketing.",
                "abstract": "some abstract...",
                "news_url": "https://example.com/news/1/",
                "thumbnail_url": "https://example.com/news/1/image.jpeg",
                "body": "Real state prices skyrocketing...",
                "category": "Society",
                "keywords": ["Society"],
            }
        }

class News(NewsBase):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    reads_count: int = Field(default=0)

# class Book(BaseModel):
#     id: str = Field(default_factory=uuid.uuid4, alias="_id")
#     title: str = Field(...)
#     author: str = Field(...)
#     synopsis: str = Field(...)

#     class Config:
#         allow_population_by_field_name = True
#         schema_extra = {
#             "example": {
#                 "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
#                 "title": "Don Quixote",
#                 "author": "Miguel de Cervantes",
#                 "synopsis": "..."
#             }
#         }

# class BookUpdate(BaseModel):
#     title: Optional[str]
#     author: Optional[str]
#     synopsis: Optional[str]

#     class Config:
#         schema_extra = {
#             "example": {
#                 "title": "Don Quixote",
#                 "author": "Miguel de Cervantes",
#                 "synopsis": "Don Quixote is a Spanish novel by Miguel de Cervantes..."
#             }
#         }
