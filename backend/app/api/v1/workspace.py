"""Bookmarks and Settings API endpoints."""
from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.core.database import get_db
from app.models.bookmark import Bookmark
from app.schemas.report import BookmarkCreate, BookmarkResponse

router = APIRouter(tags=["Workspace"])


# ─── Bookmarks ───────────────────────────────────────────────────────────────

bookmarks_router = APIRouter(prefix="/bookmarks")


@bookmarks_router.get("", response_model=List[BookmarkResponse])
async def list_bookmarks(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Bookmark)
        .where(Bookmark.user_id == current_user.id, Bookmark.deleted_at.is_(None))
        .order_by(desc(Bookmark.created_at))
    )
    return [BookmarkResponse.model_validate(b) for b in result.scalars().all()]


@bookmarks_router.post("", response_model=BookmarkResponse, status_code=201)
async def create_bookmark(
    data: BookmarkCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    bookmark = Bookmark(
        user_id=current_user.id,
        title=data.title,
        url=data.url,
        note=data.note,
        tags=data.tags,
        chat_id=data.chat_id,
        report_id=data.report_id,
    )
    db.add(bookmark)
    await db.flush()
    await db.refresh(bookmark)
    return BookmarkResponse.model_validate(bookmark)


@bookmarks_router.delete("/{bookmark_id}", status_code=204)
async def delete_bookmark(
    bookmark_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Bookmark).where(Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id)
    )
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    from datetime import datetime, timezone
    bookmark.deleted_at = datetime.now(timezone.utc)


# ─── Settings ────────────────────────────────────────────────────────────────

settings_router = APIRouter(prefix="/settings")


class UserSettingsUpdate:
    citation_style: Optional[str] = "apa"
    default_export_format: Optional[str] = "pdf"
    notification_email: Optional[bool] = True


@settings_router.get("")
async def get_settings(current_user: CurrentUser):
    return {
        "user_id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "username": current_user.username,
        "avatar_url": current_user.avatar_url,
        "is_verified": current_user.is_verified,
        "auth_provider": current_user.auth_provider,
    }


@settings_router.patch("")
async def update_settings(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    full_name: Optional[str] = None,
    avatar_url: Optional[str] = None,
):
    if full_name is not None:
        current_user.full_name = full_name
    if avatar_url is not None:
        current_user.avatar_url = avatar_url
    await db.flush()
    return {"message": "Settings updated"}
