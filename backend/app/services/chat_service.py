"""
Chat service — manages chat sessions, messages, and research orchestration.
"""
import json
from typing import AsyncGenerator, List, Optional
from uuid import UUID

import structlog
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import Chat, Message
from app.models.report import Report
from app.models.research_task import ResearchTask, Source, AgentLog, TaskStatus
from app.schemas.chat import ChatResponse, ChatDetailResponse, MessageResponse, ChatHistoryResponse

logger = structlog.get_logger(__name__)


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chat(self, user_id: UUID, title: str = "New Chat") -> Chat:
        chat = Chat(user_id=user_id, title=title)
        self.db.add(chat)
        await self.db.flush()
        await self.db.refresh(chat)
        return chat

    async def get_user_chats(
        self, user_id: UUID, page: int = 1, page_size: int = 50
    ) -> ChatHistoryResponse:
        # Count query
        count_result = await self.db.execute(
            select(func.count(Chat.id)).where(
                Chat.user_id == user_id,
                Chat.deleted_at.is_(None),
            )
        )
        total = count_result.scalar_one()

        # Paginated query
        result = await self.db.execute(
            select(Chat)
            .where(Chat.user_id == user_id, Chat.deleted_at.is_(None))
            .order_by(desc(Chat.updated_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        chats = result.scalars().all()

        return ChatHistoryResponse(
            chats=[ChatResponse.model_validate(c) for c in chats],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_chat(self, chat_id: UUID, user_id: UUID) -> Optional[Chat]:
        result = await self.db.execute(
            select(Chat)
            .options(selectinload(Chat.messages))
            .where(Chat.id == chat_id, Chat.user_id == user_id, Chat.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def add_message(
        self,
        chat_id: UUID,
        role: str,
        content: str,
        metadata: Optional[dict] = None,
        report_id: Optional[UUID] = None,
    ) -> Message:
        message = Message(
            chat_id=chat_id,
            role=role,
            content=content,
            metadata_=metadata,
            report_id=report_id,
        )
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def create_research_task(
        self, chat_id: UUID, query: str
    ) -> ResearchTask:
        task = ResearchTask(
            chat_id=chat_id,
            query=query,
            status=TaskStatus.PENDING,
        )
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def update_task_status(
        self, task_id: UUID, status: TaskStatus, plan: Optional[dict] = None, error: Optional[str] = None
    ) -> None:
        result = await self.db.execute(select(ResearchTask).where(ResearchTask.id == task_id))
        task = result.scalar_one_or_none()
        if task:
            task.status = status
            if plan:
                task.plan = plan
            if error:
                task.error_message = error

    async def save_sources(
        self, task_id: UUID, sources: List[dict]
    ) -> List[Source]:
        saved = []
        for s in sources:
            source = Source(
                task_id=task_id,
                agent_type=s.get("agent_type", "unknown"),
                title=s.get("title", "")[:500],
                authors=s.get("authors"),
                abstract=s.get("abstract"),
                summary=s.get("summary"),
                publisher=s.get("publisher"),
                doi=s.get("doi"),
                publication_date=s.get("publication_date"),
                url=s.get("url"),
                source_type=s.get("source_type"),
                confidence_score=s.get("confidence_score"),
                citation_apa=s.get("citation_apa"),
                citation_mla=s.get("citation_mla"),
                citation_chicago=s.get("citation_chicago"),
            )
            self.db.add(source)
            saved.append(source)
        await self.db.flush()
        return saved

    async def delete_chat(self, chat_id: UUID, user_id: UUID) -> bool:
        result = await self.db.execute(
            select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id)
        )
        chat = result.scalar_one_or_none()
        if not chat:
            return False
        from datetime import datetime, timezone
        chat.deleted_at = datetime.now(timezone.utc)
        return True

    async def rename_chat(self, chat_id: UUID, user_id: UUID, title: str) -> Optional[Chat]:
        result = await self.db.execute(
            select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id, Chat.deleted_at.is_(None))
        )
        chat = result.scalar_one_or_none()
        if chat:
            chat.title = title[:500]
            await self.db.flush()
        return chat
