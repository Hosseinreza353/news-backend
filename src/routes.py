from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from uuid import UUID
from typing import List, Tuple, Optional

from src.models import News, NewsBase

router = APIRouter()


@router.post(
    "/",
    response_description="Create a news",
    status_code=status.HTTP_201_CREATED,
    response_model=News,
)
def create_news(request: Request, news: NewsBase = Body(...)):
    news = News(**news.dict())
    news = jsonable_encoder(news)
    new_news = request.app.database["news"].insert_one(news)
    created_news = request.app.database["news"].find_one({"_id": new_news.inserted_id})
    return created_news


@router.get("/", response_description="List all news", response_model=List[News])
def list_news(
    request: Request, page: int = 1, size: int = 10, category: Optional[str] = None
):
    find = {}
    if category:
        find = {"category": category}
    limit = size if size >= 1 else 10
    page -= 1
    skip = 0 if page <= 0 else page * limit
    news = list(request.app.database["news"].find(find, skip=skip, limit=limit))
    return news


@router.get(
    "/categories",
    response_description="List all categories",
    response_model=List[Tuple[str, str]],
)
def get_categories(request: Request):
    cats_fa_en = {
        "Society": "جامعه",
        "Economy": "اقتصاد",
        "markets": "بازار",
        "Sport": "ورزش",
        "Politic": "سیاست",
        "International": "بین الملل",
    }
    all_categories = request.app.database["news"].find({}, {"category": 1, "_id": 0})
    cats = set()
    for cat in all_categories:
        cats.add(cat["category"])
    return [(cat, cats_fa_en[cat]) for cat in list(cats)]


@router.get("/{news_id}", response_description="Get a news detail", response_model=News)
def get_news(request: Request, news_id: UUID):
    found_news = request.app.database["news"].find_one({"_id": str(news_id)})
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
