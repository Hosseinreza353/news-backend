from fastapi import APIRouter, Body, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import PositiveInt
from math import ceil
from uuid import UUID
from typing import List, Tuple, Optional

from src.models import News, NewsBase, PaginatedNews

router = APIRouter()


@router.post(
    "/",
    response_description="Create a news",
    status_code=status.HTTP_201_CREATED,
    response_model=News,
)
async def create_news(request: Request, news: NewsBase = Body(...)):
    dbc: AsyncIOMotorDatabase = request.app._db
    news = News(**news.dict())
    news = jsonable_encoder(news)
    new_news = await dbc["news"].insert_one(news)
    created_news = await dbc["news"].find_one({"_id": new_news.inserted_id})
    return created_news


@router.get("/", response_description="List all news", response_model=PaginatedNews)
async def list_news(
    request: Request, page: PositiveInt = 1, size: PositiveInt = 10, category: Optional[str] = None
):
    dbc: AsyncIOMotorDatabase = request.app._db
    find = {}
    if category:
        find = {"category": category}
    cnt = await dbc["news"].count_documents(find)
    total_pages = ceil(cnt / size)  # cnt // size + (1 if cnt % size else 0)
    page = min(total_pages, page)
    page = max(page, 1)
    limit = size
    skip = (page-1) * limit
    # .sort('time', -1) was deleted; .find(...).sort(...).skip(...) -> find(...).skip(...)
    news = await dbc["news"].find(find, {"body": 0}).sort('time', -1).skip(skip).limit(limit).to_list(length=None)
    return PaginatedNews(items=news, total=total_pages, page=page, size=size, next=min(total_pages, page+1), prev=max(page-1, 1))


@router.get(
    "/categories",
    response_description="List all categories",
    response_model=List[Tuple[str, str]],
)
async def get_categories(request: Request):
    dbc: AsyncIOMotorDatabase = request.app._db
    cats_fa_en = {
        "Society": "جامعه",
        "Economy": "اقتصاد",
        "markets": "بازار",
        "Sport": "ورزش",
        "Politic": "سیاست",
        "International": "بین الملل",
    }
    all_categories = await dbc["news"].find({}, {"category": 1, "_id": 0}).to_list(length=None)
    cats = set()
    for cat in all_categories:
        cats.add(cat["category"])
    return [(cat, cats_fa_en[cat]) for cat in list(cats)]


@router.get("/{news_id}", response_description="Get a news detail", response_model=News)
async def get_news(request: Request, news_id: UUID):
    dbc: AsyncIOMotorDatabase = request.app._db
    found_news = await dbc["news"].find_one({"_id": str(news_id)})
    if not found_news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="news not found"
        )
    return found_news


# @router.get("/categories", response_description="List all categories")
# def get_categories(request: Request):
#     all_categories = request.app.database["news"].find({}, {"category": 1, "_id": 0})
#     print(all_categories, flush=True)
#     return "Heellloo"


# @router.post("/", response_description="Create a new book", status_code=status.HTTP_201_CREATED, response_model=Book)
# def create_book(request: Request, book: Book = Body(...)):
#     book = jsonable_encoder(book)
#     new_book = request.app.database["books"].insert_one(book)
#     created_book = request.app.database["books"].find_one(
#         {"_id": new_book.inserted_id}
#     )

#     return created_book

# @router.get("/", response_description="List all books", response_model=List[Book])
# def list_books(request: Request):
#     books = list(request.app.database["books"].find(limit=100))
#     return books

# @router.get("/{id}", response_description="Get a single book by id", response_model=Book)
# def find_book(id: str, request: Request):
#     if (book := request.app.database["books"].find_one({"_id": id})) is not None:
#         return book
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found")

# @router.put("/{id}", response_description="Update a book", response_model=Book)
# def update_book(id: str, request: Request, book: BookUpdate = Body(...)):
#     book = {k: v for k, v in book.dict().items() if v is not None}
#     if len(book) >= 1:
#         update_result = request.app.database["books"].update_one(
#             {"_id": id}, {"$set": book}
#         )

#         if update_result.modified_count == 0:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found")

#     if (
#         existing_book := request.app.database["books"].find_one({"_id": id})
#     ) is not None:
#         return existing_book

#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found")

# @router.delete("/{id}", response_description="Delete a book")
# def delete_book(id: str, request: Request, response: Response):
#     delete_result = request.app.database["books"].delete_one({"_id": id})

#     if delete_result.deleted_count == 1:
#         response.status_code = status.HTTP_204_NO_CONTENT
#         return response

#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found")
