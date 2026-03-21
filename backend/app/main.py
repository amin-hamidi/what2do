from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.routes import events, categories, venues, picks, chat, sync, health

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix=settings.API_V1_PREFIX, tags=["events"])
app.include_router(categories.router, prefix=settings.API_V1_PREFIX, tags=["categories"])
app.include_router(venues.router, prefix=settings.API_V1_PREFIX, tags=["venues"])
app.include_router(picks.router, prefix=settings.API_V1_PREFIX, tags=["picks"])
app.include_router(chat.router, prefix=settings.API_V1_PREFIX, tags=["chat"])
app.include_router(sync.router, prefix=settings.API_V1_PREFIX, tags=["sync"])
app.include_router(health.router, tags=["health"])
