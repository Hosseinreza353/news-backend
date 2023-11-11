from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.cors import CORSMiddleware

from src import utils
from src.routes import router as news_router

app = FastAPI()

app.add_event_handler("startup", utils.create_start_app_handler(app))
app.add_event_handler("shutdown", utils.create_stop_app_handler(app))

app.include_router(news_router, tags=["news"], prefix="/news")

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://172.28.1.1:3000",
    "http://0.0.0.0:3000",
    "http://185.110.188.75:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# app.add_event_handler("startup", utils.create_start_app_handler(app))
# app.add_event_handler("shutdown", utils.create_stop_app_handler(app))

# app.include_router(news_router, tags=["news"], prefix="/news")

