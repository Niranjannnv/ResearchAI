"""Chat and Message schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class MessageResponse(BaseModel):
    id: UUID
    chat_id: UUID
    role: str
    content: str
    token_count: Optional[int]
    metadata_: Optional[Dict[str, Any]] = None
    report_id: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    id: UUID
    title: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    model_config = {"from_attributes": True}


class ChatDetailResponse(ChatResponse):
    messages: List[MessageResponse] = []

    model_config = {"from_attributes": True}


class CreateChatRequest(BaseModel):
    title: Optional[str] = "New Chat"


class RenameChatRequest(BaseModel):
    title: str


class SendMessageRequest(BaseModel):
    content: str
    stream: bool = True


class ChatHistoryResponse(BaseModel):
    chats: List[ChatResponse]
    total: int
    page: int
    page_size: int
