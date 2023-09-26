from redis import Redis
from pymongo import MongoClient

from src import config, redis_consumer, handlers

class MessageBus:
    def __init__(self):
        self.config = config.Config()
        mongo_conf = self.config.mongodb
        # mongo_conn_str = f"mongodb://{mongo_conf.user}:{mongo_conf.password}@{mongo_conf.host}:{mongo_conf.port}"
        mongo_conn_str = "mongodb://%s:%s@%s:%d" % (
            mongo_conf.user,
            mongo_conf.password,
            mongo_conf.host,
            mongo_conf.port,
        )
        self.mongodb_client = MongoClient(mongo_conn_str)
        self.db = self.mongodb_client[mongo_conf.db]

        redis_config = self.config.redis
        redis_conn = Redis(
            host=redis_config.host,
            port=redis_config.port,
            db=redis_config.db,
            password=redis_config.password,
            decode_responses=True,
            encoding="utf-8",
        )

        self.redis_consumer = redis_consumer.RedisConsumer(
            redis_conn, redis_config.topic, handler=lambda news: handlers.add_news(self.db, news)
        )
