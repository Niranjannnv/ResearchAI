"""User ORM model."""
import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.chat import Chat
    from app.models.bookmark import Bookmark
    from app.models.report import Report


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Auth
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # OAuth
    google_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True, index=True)
    auth_provider: Mapped[str] = mapped_column(String(50), default="email", nullable=False)

    # Email verification
    email_verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    chats: Mapped[List["Chat"]] = relationship("Chat", back_populates="user", lazy="select")
    bookmarks: Mapped[List["Bookmark"]] = relationship("Bookmark", back_populates="user", lazy="select")
    reports: Mapped[List["Report"]] = relationship("Report", back_populates="user", lazy="select")

    def __repr__(self) -> str:
        return f"<User {self.email}>"
