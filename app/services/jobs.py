import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, delete

from app.models.job import Job, JobArtifact

def create_job(db: Session, user_id, job_type: str, payload: dict) -> Job:
    job = Job(
        status="queued",
        job_type=job_type,
        user_id=user_id,
        updated_at=datetime.utcnow(),
    )
    artifact = JobArtifact(job=job, input=payload, meta={})
    db.add(job)
    db.add(artifact)
    db.commit()
    db.refresh(job)
    return job

def list_jobs(db: Session, user_id, limit: int, offset: int, status: str | None):
    stmt = select(Job).where(Job.user_id == user_id)
    if status:
        stmt = stmt.where(Job.status == status)
    stmt = stmt.order_by(desc(Job.created_at)).limit(limit).offset(offset)
    return list(db.scalars(stmt).all())

def delete_job(db: Session, job: Job) -> None:
    db.delete(job)
    db.commit()

def get_job(db: Session, job_id: uuid.UUID) -> Job | None:
    return db.get(Job, job_id)
