import uuid
import app.models.user  # ensures User model is registered
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db, Base, engine
from app.schemas.job import JobSubmit, JobResponse
from app.services.jobs import create_job, get_job
from worker.tasks import run_job  # shared task definition

app = FastAPI(title="gpu-job-management-api")
app.include_router(auth_router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/jobs", response_model=JobResponse)
def submit_job(req: JobSubmit, db: Session = Depends(get_db)):
    job = create_job(db, req.job_type, req.payload)
    run_job.delay(str(job.id))
    return JobResponse(id=str(job.id), status=job.status, job_type=job.job_type)

@app.get("/jobs/{job_id}", response_model=JobResponse)
def job_status(job_id: str, db: Session = Depends(get_db)):
    try:
        jid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job_id")

    job = get_job(db, jid)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    result = None
    if job.artifacts and job.artifacts.output is not None:
        result = job.artifacts.output

    return JobResponse(
        id=str(job.id),
        status=job.status,
        job_type=job.job_type,
        result=result,
        error=job.error,
    )

# Sprint shortcut: create tables automatically.
# Later we’ll replace this with Alembic migrations.
@app.on_event("startup")
def _create_tables():
    Base.metadata.create_all(bind=engine)
