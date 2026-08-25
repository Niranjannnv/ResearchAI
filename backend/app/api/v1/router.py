"""Main API v1 router — aggregates all sub-routers."""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.reports import router as reports_router
from app.api.v1.workspace import bookmarks_router, settings_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(reports_router)
api_router.include_router(bookmarks_router)
api_router.include_router(settings_router)
