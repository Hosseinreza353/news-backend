from __future__ import annotations
import os
import json
import threading
from redis.asyncio import Redis
from pathlib import Path
from dotenv import dotenv_values
from collections import namedtuple

# Getting redis configs from an env file
HOME = Path(__file__).resolve().parents[2]
ENV_CONFS = dotenv_values(f"{HOME / os.environ.get('ENV_FILE', '.env.local')}")
RedisConf = namedtuple("RedisConf", ['host', 'port', 'db', 'password', 'topic'])
redis_config = RedisConf(
    ENV_CONFS.get("REDIS_HOST", "localhost"),
    ENV_CONFS.get("REDIS_PORT", 6379),
    int(ENV_CONFS.get("REDIS_DB", 0)),
    ENV_CONFS.get("REDIS_PASSWORD", "test"),
    ENV_CONFS.get("REDIS_TOPIC", "news")
)
# print(redis_config, flush=True)

class RedisMixin(object):
    rc = None
    topic = ""
    _lock = threading.RLock()
    def __new__(cls, *args, **kwargs):
        with RedisMixin._lock:
            # if 'rc' not in cls.__dict__:
            if not RedisMixin.rc:
                RedisMixin.rc = Redis(
                    host=redis_config.host,
                    port=redis_config.port,
                    db=redis_config.db,
                    password=redis_config.password,
                    decode_responses=True,
                    encoding="utf-8",
                )
                RedisMixin.topic = redis_config.topic
        return super().__new__(cls, *args, **kwargs)

    @property
    def redis(self) -> Redis:
        # if not hasattr(self, "__redis_conn"):
        #     self.__redis_conf = redis_config
        #     self.__redis_conn = Redis(
        #         host=self.__redis_conf.host,
        #         port=self.__redis_conf.port,
        #         db=self.__redis_conf.db,
        #         password=self.__redis_conf.password,
        #         decode_responses=True,
        #         encoding="utf-8",
        #     )
        #     print(self.__redis_conn.keys("*"))
        if not isinstance(self.rc, Redis) or not self.topic:
            raise AttributeError("redis client doesn't exist/topic is empty")
        return self.rc

    async def publish(self, payload):
        await self.rc.publish(self.topic, json.dumps(payload))
    
    async def update_last_news_dts(self, last_news_dts: dict):
        await self.rc.hset("last_news_dts", mapping=last_news_dts)

rm = RedisMixin()
