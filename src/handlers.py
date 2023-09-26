from pymongo import database
from src import models

def add_news(db: database.Database, news: models.NewsBase):
    # news = models.News(**news.dict())
    # news = jsonable_encoder(news)
    # new_news = request.app.database["news"].insert_one(news)
    # created_news = request.app.database["news"].find_ond(
    #     {"_id": new_news.inserted_id}
    # )
    ...
