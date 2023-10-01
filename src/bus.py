from redis.asyncio import Redis
from motor.motor_asyncio import AsyncIOMotorClient

from src import config, redis_consumer, handlers, scheduler

class MessageBus:
    def __init__(self):
        self.config = config.Config()
        mongo_conf = self.config.mongodb
        mongo_conn_str = "mongodb://%s:%s@%s:%d" % (
            mongo_conf.user,
            mongo_conf.password,
            mongo_conf.host,
            mongo_conf.port,
        )
        self.db_client = AsyncIOMotorClient(mongo_conn_str, maxPoolSize=10, minPoolSize=10)
        self.db = self.db_client[mongo_conf.db]

        redis_config = self.config.redis
        self.rc = Redis(
            host=redis_config.host,
            port=redis_config.port,
            db=redis_config.db,
            password=redis_config.password,
            decode_responses=True,
            encoding="utf-8",
        )

        self.redis_consumer = redis_consumer.RedisConsumer(
            self.rc, redis_config.topic, handler=lambda news: handlers.add_news(self.db, news)
        )

        self.scheduler = scheduler.Scheduler()
