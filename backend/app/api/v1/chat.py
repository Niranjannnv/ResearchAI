"""
Chat API endpoints — CRUD for chats and real-time SSE streaming of research.
"""
import json
from typing import Annotated, Optional
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.core.database import get_db
from app.models.research_task import TaskStatus
from app.schemas.chat import (
    ChatDetailResponse,
    ChatHistoryResponse,
    ChatResponse,
    CreateChatRequest,
    MessageResponse,
    RenameChatRequest,
    SendMessageRequest,
)
from app.services.chat_service import ChatService

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/chats", tags=["Chat"])


@router.get("", response_model=ChatHistoryResponse)
async def list_chats(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = 1,
    page_size: int = 50,
):
    """Get paginated chat history for the current user."""
    service = ChatService(db)
    return await service.get_user_chats(current_user.id, page=page, page_size=page_size)


@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    data: CreateChatRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new chat session."""
    service = ChatService(db)
    chat = await service.create_chat(current_user.id, title=data.title or "New Chat")
    return ChatResponse.model_validate(chat)


@router.get("/{chat_id}", response_model=ChatDetailResponse)
async def get_chat(
    chat_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a specific chat with all messages."""
    try:
        parsed_id = UUID(chat_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=404, detail="Chat not found")
    service = ChatService(db)
    chat = await service.get_chat(parsed_id, current_user.id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return ChatDetailResponse.model_validate(chat)


@router.patch("/{chat_id}", response_model=ChatResponse)
async def rename_chat(
    chat_id: str,
    data: RenameChatRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Rename a chat session."""
    try:
        parsed_id = UUID(chat_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid chat ID")
    service = ChatService(db)
    chat = await service.rename_chat(parsed_id, current_user.id, data.title)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return ChatResponse.model_validate(chat)


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Soft-delete a chat session."""
    try:
        parsed_id = UUID(chat_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=404, detail="Chat not found")
    service = ChatService(db)
    deleted = await service.delete_chat(parsed_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Chat not found")


@router.post("/{chat_id}/messages")
async def send_message(
    chat_id: str,
    data: SendMessageRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Send a message to the Mother Agent and receive a streaming SSE response.
    The agent runs the full research pipeline and streams progress events.
    """
    from app.agents.mother_agent import stream_research

    service = ChatService(db)
    if chat_id == "new":
        chat = await service.create_chat(current_user.id, title=data.content[:60])
        real_chat_id = chat.id
    else:
        try:
            parsed_id = UUID(chat_id)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid chat ID")
        chat = await service.get_chat(parsed_id, current_user.id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        real_chat_id = parsed_id

    # Save user message
    user_message = await service.add_message(
        chat_id=real_chat_id, role="user", content=data.content
    )

    # Create research task record
    task = await service.create_research_task(chat_id=real_chat_id, query=data.content)
    await db.commit()

    async def event_stream():
        """SSE generator — streams research progress and final report."""
        try:
            # Update task to running
            await service.update_task_status(task.id, TaskStatus.RUNNING)
            await db.commit()

            # Track collected report data
            final_report = None
            all_sources = []
            all_citations = []

            async for event in stream_research(
                query=data.content,
                chat_id=str(real_chat_id),
                user_id=str(current_user.id),
            ):
                if event["type"] == "status":
                    event["chat_id"] = str(real_chat_id)
                    yield f"data: {json.dumps(event)}\n\n"

                elif event["type"] == "complete":
                    final_report = event.get("report")
                    all_sources = event.get("sources", [])
                    all_citations = event.get("citations", [])

                    # Save sources to DB
                    if all_sources:
                        await service.save_sources(task.id, all_sources)

                    # Generate report files
                    if final_report:
                        from app.services.report_service import report_generator
                        from app.models.report import Report

                        title = (final_report.get("research_question") or data.content)[:500]
                        paths = await report_generator.generate_all(
                            report_id=task.id,
                            content=final_report,
                            title=title,
                            query=data.content,
                        )

                        db_report = Report(
                            user_id=current_user.id,
                            task_id=task.id,
                            chat_id=real_chat_id,
                            title=title,
                            query=data.content,
                            summary=final_report.get("executive_summary", "")[:1000],
                            content=final_report,
                            pdf_path=paths.get("pdf"),
                            docx_path=paths.get("docx"),
                            markdown_path=paths.get("markdown"),
                            html_path=paths.get("html"),
                            source_count=len(all_sources),
                        )
                        db.add(db_report)
                        await db.flush()
                        await db.refresh(db_report)

                        # Save assistant message with full report reference and rich metadata
                        assistant_content = final_report.get("executive_summary", "Research complete.")
                        await service.add_message(
                            chat_id=real_chat_id,
                            role="assistant",
                            content=assistant_content,
                            metadata={
                                "sources": all_sources[:20],
                                "citations": all_citations[:20],
                                "report_id": str(db_report.id),
                                "report": final_report,
                            },
                            report_id=db_report.id,
                        )

                        await service.update_task_status(task.id, TaskStatus.COMPLETED, plan=None)
                        await db.commit()

                        yield f"data: {json.dumps({'type': 'complete', 'chat_id': str(real_chat_id), 'report': final_report, 'report_id': str(db_report.id), 'sources': all_sources[:10], 'citations': all_citations})}\n\n"
                    else:
                        await service.update_task_status(task.id, TaskStatus.COMPLETED)
                        await db.commit()
                        yield f"data: {json.dumps({'type': 'complete', 'chat_id': str(real_chat_id), 'report': None})}\n\n"

        except Exception as e:
            logger.error("Stream error", error=str(e), chat_id=str(real_chat_id))
            await service.update_task_status(task.id, TaskStatus.FAILED, error=str(e))
            await db.commit()
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
