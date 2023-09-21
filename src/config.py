import os
from collections import namedtuple
from dotenv import dotenv_values

MongoDBConf = namedtuple("MongoDBConf", ['host', 'port', 'user', 'password', 'db'])
RedisConf = namedtuple("RedisConf", ['host', 'port', 'db', 'password', 'topic'])
MinIOConf = namedtuple("MinIOConf", ['endpoint', 'access_key', 'secret_key'])

class Config:
    def __init__(self):
        dotenv_path = os.environ.get("ENV_FILE", ".env.local")
        # print(dotenv_path)
        if dotenv_path:
            self.config = dotenv_values(dotenv_path)
        # print(self.config)
    
    @property
    def mongodb(self) -> MongoDBConf:
        host = self.config["MONGO_HOST"]
        port = int(self.config["MONGO_PORT"])
        user = self.config["MONGO_USER"]
        password = self.config["MONGO_PASS"]
        db = self.config["MONGO_DB"]
        return MongoDBConf(host, port, user, password, db)

    @property
    def redis(self) -> RedisConf:
        host = self.config["REDIS_HOST"]
        port = int(self.config["REDIS_PORT"])
        db = int(self.config["REDIS_DB"])
        password = self.config["REDIS_PASSWORD"]
        topic = self.config["REDIS_TOPIC"]
        return RedisConf(host, port, db, password, topic)

    @property
    def minio(self) -> MinIOConf:
        endpoint = self.config["MINIO_ENDPOINT"]
        access_key = self.config["MINIO_ACCESS_KEY"]
        secret_key = self.config["MINIO_SECRET_KEY"]
        return MinIOConf(endpoint, access_key, secret_key)
