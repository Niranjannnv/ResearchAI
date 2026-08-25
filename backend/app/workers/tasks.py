"""Background Celery tasks for async research processing."""
import asyncio
from datetime import datetime, timezone, timedelta

import structlog

from app.workers.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(bind=True, name="run_research_task")
def run_research_task(self, query: str, chat_id: str, user_id: str, task_db_id: str):
    """
    Background task: run full research pipeline.
    Called when streaming isn't needed (e.g., scheduled research).
    """
    async def _run():
        from app.agents.mother_agent import run_research
        return await run_research(query=query, chat_id=chat_id, user_id=user_id)

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_run())
        logger.info("Research task completed", task_id=self.request.id)
        return {"status": "completed", "source_count": len(result.get("ranked_results", []))}
    except Exception as exc:
        logger.error("Research task failed", error=str(exc), task_id=self.request.id)
        self.retry(exc=exc, countdown=60, max_retries=2)
    finally:
        loop.close()


@celery_app.task(name="cleanup_old_reports")
def cleanup_old_reports():
    """Remove report files older than 30 days from disk."""
    import os
    from pathlib import Path
    from app.core.config import settings

    reports_dir = Path(settings.REPORTS_DIR)
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    cleaned = 0

    for report_dir in reports_dir.iterdir():
        if report_dir.is_dir():
            mtime = datetime.fromtimestamp(report_dir.stat().st_mtime, tz=timezone.utc)
            if mtime < cutoff:
                import shutil
                shutil.rmtree(str(report_dir), ignore_errors=True)
                cleaned += 1

    logger.info("Cleaned up old reports", count=cleaned)
    return {"cleaned": cleaned}
