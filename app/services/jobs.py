import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.job import Job, JobArtifact

def create_job(db: Session, job_type: str, payload: dict) -> Job:
    job = Job(status="queued", job_type=job_type, updated_at=datetime.utcnow())
    artifact = JobArtifact(job=job, input=payload, meta={})
    db.add(job)
    db.add(artifact)
    db.commit()
    db.refresh(job)
    return job

def get_job(db: Session, job_id: uuid.UUID) -> Job | None:
    return db.get(Job, job_id)
