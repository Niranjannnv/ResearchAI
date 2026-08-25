"""Report schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class ReportSection(BaseModel):
    title: str
    content: str
    subsections: List["ReportSection"] = []


class ReportContent(BaseModel):
    executive_summary: str
    research_question: str
    methodology: str
    findings: List[Dict[str, Any]]
    analysis: str
    comparisons: Optional[List[Dict[str, Any]]] = None
    conflicts: Optional[List[Dict[str, Any]]] = None
    references: List[Dict[str, Any]]
    appendix: Optional[str] = None


class ReportResponse(BaseModel):
    id: UUID
    title: str
    query: str
    summary: Optional[str]
    content: Optional[Dict[str, Any]]
    source_count: Optional[int]
    word_count: Optional[int]
    citation_style: str
    is_public: bool
    has_pdf: bool
    has_docx: bool
    has_markdown: bool
    has_html: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_paths(cls, report) -> "ReportResponse":
        return cls(
            id=report.id,
            title=report.title,
            query=report.query,
            summary=report.summary,
            content=report.content,
            source_count=report.source_count,
            word_count=report.word_count,
            citation_style=report.citation_style,
            is_public=report.is_public,
            has_pdf=bool(report.pdf_path),
            has_docx=bool(report.docx_path),
            has_markdown=bool(report.markdown_path),
            has_html=bool(report.html_path),
            created_at=report.created_at,
            updated_at=report.updated_at,
        )


class ReportListResponse(BaseModel):
    reports: List[ReportResponse]
    total: int


class BookmarkCreate(BaseModel):
    title: str
    url: Optional[str] = None
    note: Optional[str] = None
    tags: Optional[List[str]] = None
    chat_id: Optional[UUID] = None
    report_id: Optional[UUID] = None


class BookmarkResponse(BaseModel):
    id: UUID
    title: str
    url: Optional[str]
    note: Optional[str]
    tags: Optional[List[str]]
    chat_id: Optional[UUID]
    report_id: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}
