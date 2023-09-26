import os
import json
from redis import Redis
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
    ENV_CONFS.get("REDIS_TOPIC", "news_topic")
)

class RedisMixin(object):
    @property
    def redis(self) -> Redis:
        if not hasattr(self, "__redis_conn"):
            self.__redis_conf = redis_config
            self.__redis_conn = Redis(
                host=self.__redis_conf.host,
                port=self.__redis_conf.port,
                db=self.__redis_conf.db,
                password=self.__redis_conf.password,
                decode_responses=True,
                encoding="utf-8",
            )
            # print(self.__redis_conn.keys("*"))
        return self.__redis_conn

    def publish(self, payload):
        self.__redis_conn.publish(self.__redis_conf.topic, json.dumps(payload))
