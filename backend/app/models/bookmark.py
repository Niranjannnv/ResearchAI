"""Bookmark ORM model."""
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class Bookmark(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "bookmarks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Reference to chat/message/report
    chat_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("chats.id", ondelete="SET NULL"), nullable=True
    )
    report_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("reports.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="bookmarks")

    def __repr__(self) -> str:
        return f"<Bookmark {self.title[:50]}>"
