"""ResearchTask and Source ORM models."""
import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, Text, Float, JSON, Enum, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.chat import Chat


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResearchTask(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "research_tasks"

    chat_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        String(20), default=TaskStatus.PENDING, nullable=False
    )
    plan: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    celery_task_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    chat: Mapped["Chat"] = relationship("Chat", back_populates="research_tasks")
    sources: Mapped[List["Source"]] = relationship("Source", back_populates="task", lazy="select")
    agent_logs: Mapped[List["AgentLog"]] = relationship("AgentLog", back_populates="task", lazy="select")

    def __repr__(self) -> str:
        return f"<ResearchTask {self.status}: {self.query[:50]}>"


class Source(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "sources"

    task_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("research_tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "academic", "medical"

    # Core metadata
    title: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # list of author names
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    publisher: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    doi: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    publication_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    citation_apa: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    citation_mla: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    citation_chicago: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Raw API response for auditing
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    task: Mapped["ResearchTask"] = relationship("ResearchTask", back_populates="sources")

    def __repr__(self) -> str:
        return f"<Source {self.title[:50]}>"


class AgentLog(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "agent_logs"

    task_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("research_tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    results_count: Mapped[Optional[int]] = mapped_column(nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)

    # Relationships
    task: Mapped["ResearchTask"] = relationship("ResearchTask", back_populates="agent_logs")
