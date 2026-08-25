"""Reports API — download and manage research reports."""
import mimetypes
import os
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import FileResponse
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.core.database import get_db
from app.models.report import Report
from app.schemas.report import ReportListResponse, ReportResponse

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("", response_model=ReportListResponse)
async def list_reports(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = 1,
    page_size: int = 20,
):
    """List all reports for the current user."""
    from sqlalchemy import func
    count_result = await db.execute(
        select(func.count(Report.id)).where(
            Report.user_id == current_user.id, Report.deleted_at.is_(None)
        )
    )
    total = count_result.scalar_one()

    result = await db.execute(
        select(Report)
        .where(Report.user_id == current_user.id, Report.deleted_at.is_(None))
        .order_by(desc(Report.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    reports = result.scalars().all()

    return ReportListResponse(
        reports=[ReportResponse.from_orm_with_paths(r) for r in reports],
        total=total,
    )


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a specific report."""
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.user_id == current_user.id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportResponse.from_orm_with_paths(report)


@router.get("/{report_id}/download/{format}")
async def download_report(
    report_id: str,
    format: str = Path(..., pattern="^(pdf|docx|markdown|html)$"),
    current_user: CurrentUser = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """Download a report in the specified format with on-demand generation fallback."""
    import json
    import uuid as uuid_pkg
    from app.services.report_service import report_generator

    parsed_uuid = None
    try:
        parsed_uuid = uuid_pkg.UUID(report_id)
    except Exception:
        pass

    query = select(Report).where(
        (Report.id == parsed_uuid) if parsed_uuid else (Report.id == report_id),
        Report.user_id == current_user.id,
    )
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    path_map = {
        "pdf": report.pdf_path,
        "docx": report.docx_path,
        "markdown": report.markdown_path,
        "html": report.html_path,
    }

    file_path = path_map.get(format)
    # If file is not present or missing from disk, generate it dynamically
    if not file_path or not os.path.exists(file_path):
        try:
            content = report.content if isinstance(report.content, dict) else json.loads(report.content or "{}")
            file_path = report_generator.generate_single_format(
                report_id=report.id,
                format_name=format,
                content=content,
                title=report.title or "Research Report",
                query=report.query or "",
            )
            if format == "pdf":
                report.pdf_path = file_path
            elif format == "docx":
                report.docx_path = file_path
            elif format == "markdown":
                report.markdown_path = file_path
            elif format == "html":
                report.html_path = file_path
            await db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate {format} file: {str(e)}")

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Report in {format} format could not be generated")

    ext_map = {"pdf": ".pdf", "docx": ".docx", "markdown": ".md", "html": ".html"}
    content_type_map = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "markdown": "text/markdown",
        "html": "text/html",
    }

    safe_title = "".join(c for c in (report.title or "ResearchReport")[:50] if c.isalnum() or c in " -_").strip()
    filename = f"{safe_title}{ext_map[format]}"

    return FileResponse(
        path=file_path,
        media_type=content_type_map[format],
        filename=filename,
    )


@router.delete("/{report_id}", status_code=204)
async def delete_report(
    report_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Soft-delete a report."""
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.user_id == current_user.id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    from datetime import datetime, timezone
    report.deleted_at = datetime.now(timezone.utc)
