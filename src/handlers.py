from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase

from src import models


async def add_news(db: AsyncIOMotorDatabase, news: models.NewsBase | dict):
    news_dict = news if isinstance(news, dict) else news.dict()
    news = models.News(**news_dict)
    news = jsonable_encoder(news)
    new_news = await db["news"].insert_one(news)
    return new_news.inserted_id
