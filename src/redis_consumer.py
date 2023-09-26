import json
from redis import Redis


class RedisConsumer:
    def __init__(self, redis_conn: Redis, topic, *, handler=None):
        self.redis_conn = redis_conn
        self.topic = topic
        self.handler = handler
    
    def run(self):
        try:
            pubsub = self.redis_conn.pubsub()
            pubsub.subscribe(self.topic)
            for msg in pubsub.listen():
                if msg["type"] == "message":
                    self.handler(json.loads(msg["data"]))
        except Exception as e:
            print(f"{e}")
