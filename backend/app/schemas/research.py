"""Research and Source schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SourceResult(BaseModel):
    """Structured result returned by every child agent."""
    title: str
    authors: List[str] = Field(default_factory=list)
    abstract: Optional[str] = None
    summary: Optional[str] = None
    publisher: Optional[str] = None
    doi: Optional[str] = None
    publication_date: Optional[str] = None
    url: Optional[str] = None
    source_type: Optional[str] = None
    agent_type: str
    confidence_score: float = Field(default=0.5, ge=0.0, le=1.0)
    citation_apa: Optional[str] = None
    citation_mla: Optional[str] = None
    citation_chicago: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


class ResearchPlan(BaseModel):
    """Mother Agent's execution plan."""
    query: str
    domain: str
    sub_queries: List[str]
    agents_to_use: List[str]
    reasoning: str


class ResearchTaskResponse(BaseModel):
    id: UUID
    chat_id: UUID
    query: str
    domain: Optional[str]
    status: str
    plan: Optional[Dict[str, Any]]
    created_at: datetime

    model_config = {"from_attributes": True}


class SourceResponse(BaseModel):
    id: UUID
    task_id: UUID
    agent_type: str
    title: str
    authors: Optional[List[str]]
    abstract: Optional[str]
    summary: Optional[str]
    publisher: Optional[str]
    doi: Optional[str]
    publication_date: Optional[str]
    url: Optional[str]
    source_type: Optional[str]
    confidence_score: Optional[float]
    citation_apa: Optional[str]
    citation_mla: Optional[str]
    citation_chicago: Optional[str]

    model_config = {"from_attributes": True}


class AgentLogResponse(BaseModel):
    id: UUID
    agent_name: str
    action: str
    status: str
    duration_ms: Optional[float]
    results_count: Optional[int]
    error: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
