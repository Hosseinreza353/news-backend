import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from redis.asyncio import Redis
import tenacity
import json
import httpx

from src.config import Config
from src.routes import router as news_router

config = Config()

app = FastAPI()
# SETTING MONGO UP
mongo_conf = config.mongodb
# mongo_conn_str = f"mongodb://{mongo_conf.user}:{mongo_conf.pass_}@{mongo_conf.host}:{mongo_conf.port}"
mongo_conn_str = "mongodb://%s:%s@%s:%d" % (
    mongo_conf.user,
    mongo_conf.password,
    mongo_conf.host,
    mongo_conf.port,
)
app.mongodb_client = MongoClient(mongo_conn_str)
app.database = app.mongodb_client[mongo_conf.db]
# ALSO REDIS
redis_conf = config.redis
redis_conn = Redis(
    host=redis_conf.host,
    port=redis_conf.port,
    db=redis_conf.db,
    password=redis_conf.password,
    decode_responses=True,
    encoding="utf-8",
)
app.redis = redis_conn
app.redis_consumer_task = None

@app.on_event("startup")
def startup_event():
    # mongo_conf = config.mongodb
    # mongo_conn_str = f"mongodb://{mongo_conf.user}:{mongo_conf.password}@{mongo_conf.host}:{mongo_conf.port}"
    # app.mongodb_client = MongoClient(mongo_conn_str)
    # app.database = app.mongodb_client[mongo_conf.db]
    # print("Connected to the MongoDB database! brilliant...")
    app.redis_consumer_task = asyncio.create_task(redis_consumer(app))

@app.on_event("shutdown")
def shutdown_event():
    app.mongodb_client.close()
    try:
        app.redis_consumer_task.cancel()
    except Exception as e:
        pass

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news_router, tags=["news"], prefix="/news")

MAX_IN_PARALLEL = 10
limit_sem = asyncio.Semaphore(MAX_IN_PARALLEL)

async def post_create_news(client, url, data):
    async with limit_sem:
        response = await client.post(url, json=data)
        return response.status_code

async def redis_consumer(app: FastAPI):
    @tenacity.retry(
        sleep=asyncio.sleep,
        wait=tenacity.wait_random_exponential(multiplier=1, max=60),
        # stop=tenacity.stop_after_attempt(10),
        reraise=True,
    )
    async def check_redis(app):
        if not hasattr(app, "redis"):
            raise Exception("app doesn't have redis connection setup.")
        else:
            await getattr(app, "redis").ping()
    try:
        await check_redis(app)
    except Exception as e:
        return
    client = httpx.AsyncClient()
    url = app.url_path_for('create_news')
    send_request = lambda data: post_create_news(client, url, data)
    pubsub = app.redis.pubsub()
    await pubsub.subscribe(redis_conf.topic)
    try:
        async for msg in pubsub.listen():
            if msg["type"] == "message":
                print(await send_request(json.loads(msg["data"])))
    except asyncio.CancelledError as e:
        pass
