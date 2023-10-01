import asyncio
import json
from redis.asyncio import Redis
from typing import Awaitable
# import threading


class RedisConsumer:
    def __init__(self, redis_conn: Redis, topic: str, *, handler: Awaitable=None):
        self.redis_conn = redis_conn
        self.topic = topic
        self.handler = handler
    
    async def start(self):
        try:
            pubsub = self.redis_conn.pubsub()
            await pubsub.subscribe(self.topic)
            async for msg in pubsub.listen():
                if msg["type"] == "message":
                    # print(threading.get_ident(), end=" | ")
                    print("+Consumed data from redis", flush=True)
                    await self.handler(json.loads(msg["data"]))
        except asyncio.CancelledError as e:
            print("Redis consumer stopped.")
        except Exception as e:
            print(f"{e}")


# MAX_IN_PARALLEL = 10
# limit_sem = asyncio.Semaphore(MAX_IN_PARALLEL)

# async def post_create_news(client, url, data):
#     async with limit_sem:
#         response = await client.post(url, json=data)
#         return response.status_code

# async def redis_consumer(app: FastAPI):
#     @tenacity.retry(
#         sleep=asyncio.sleep,
#         wait=tenacity.wait_random_exponential(multiplier=1, max=60),
#         # stop=tenacity.stop_after_attempt(10),
#         reraise=True,
#     )
#     async def check_redis(app):
#         if not hasattr(app, "redis"):
#             raise Exception("app doesn't have redis connection setup.")
#         else:
#             await getattr(app, "redis").ping()
#     try:
#         await check_redis(app)
#     except Exception as e:
#         return
#     client = httpx.AsyncClient()
#     url = app.url_path_for('create_news')
#     send_request = lambda data: post_create_news(client, url, data)
#     pubsub = app.redis.pubsub()
#     await pubsub.subscribe(redis_conf.topic)
#     try:
#         async for msg in pubsub.listen():
#             if msg["type"] == "message":
#                 print(await send_request(json.loads(msg["data"])))
#     except asyncio.CancelledError as e:
#         pass
