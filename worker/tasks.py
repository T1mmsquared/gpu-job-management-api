import uuid
import time
import app.models  # noqa: F401
from datetime import datetime

from sqlalchemy.orm import Session

from worker.celery_app import celery_app
from app.core.db import SessionLocal
from app.models.job import Job

def _db() -> Session:
    return SessionLocal()

@celery_app.task(name="run_job")
def run_job(job_id: str):
    db = _db()
    try:
        jid = uuid.UUID(job_id)
        job: Job | None = db.get(Job, jid)
        if not job:
            return

        job.status = "running"
        job.started_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(job)

        payload = job.artifacts.input if job.artifacts else {}

        if job.job_type == "test_sleep":
            seconds = int(payload.get("seconds", 5))
            seconds = max(0, min(seconds, 60))
            time.sleep(seconds)
            job.artifacts.output = {"slept_seconds": seconds}

        elif job.job_type == "validate_payload":
            required = payload.get("required_value")
            if required is None:
                raise ValueError("payload.required_value is required")
            job.artifacts.output = {"valid": True, "required_value": required}

        else:
            raise ValueError(f"Unsupported job_type: {job.job_type}")

        job.status = "succeeded"
        job.finished_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
        job.error = None
        db.commit()

    except Exception as e:
        db.rollback()
        try:
            job = db.get(Job, uuid.UUID(job_id))
            if job:
                job.status = "failed"
                job.finished_at = datetime.utcnow()
                job.updated_at = datetime.utcnow()
                job.error = str(e)
                db.commit()
        finally:
            pass
        raise
    finally:
        db.close()
