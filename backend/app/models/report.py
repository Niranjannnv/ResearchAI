"""Report ORM model."""
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class Report(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "reports"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("research_tasks.id", ondelete="SET NULL"), nullable=True, index=True
    )
    chat_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("chats.id", ondelete="SET NULL"), nullable=True, index=True
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Report content stored as structured JSON
    content: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # File paths for exports
    pdf_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    docx_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    markdown_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    html_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Statistics
    source_count: Mapped[Optional[int]] = mapped_column(nullable=True)
    word_count: Mapped[Optional[int]] = mapped_column(nullable=True)
    citation_style: Mapped[str] = mapped_column(String(20), default="apa", nullable=False)

    is_public: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="reports")

    def __repr__(self) -> str:
        return f"<Report {self.title[:50]}>"
