from pymongo import MongoClient

from src import config

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
