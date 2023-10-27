from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src import utils
from src.routes import router as news_router

app = FastAPI()

app.add_event_handler("startup", utils.create_start_app_handler(app))
app.add_event_handler("shutdown", utils.create_stop_app_handler(app))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news_router, tags=["news"], prefix="/news")
