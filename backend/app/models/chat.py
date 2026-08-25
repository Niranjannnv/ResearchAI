"""Chat and Message ORM models."""
import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, Text, Integer, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.research_task import ResearchTask


class Chat(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "chats"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False, default="New Chat")
    is_archived: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="chats")
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="chat", order_by="Message.created_at", lazy="select"
    )
    research_tasks: Mapped[List["ResearchTask"]] = relationship(
        "ResearchTask", back_populates="chat", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Chat {self.title[:30]}>"


class Message(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "messages"

    chat_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # "user" | "assistant" | "system"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Structured metadata (citations, sources, etc.)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)

    # If this message has an associated report
    report_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("reports.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message {self.role}: {self.content[:50]}>"
