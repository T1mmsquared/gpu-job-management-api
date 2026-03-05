import uuid
from app.models.user import User  # ensures User model is registered
from typing import Optional
from fastapi import Query
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db, Base, engine
from app.core.deps import get_current_user
from app.schemas.job import JobSubmit, JobResponse
from app.services.jobs import create_job, get_job, list_jobs, delete_job
from app.routes.auth import router as auth_router
from worker.tasks import run_job  # shared task definition

app = FastAPI(title="gpu-job-management-api")
app.include_router(auth_router)

@app.on_event("startup")
def _create_tables():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/jobs", response_model=JobResponse)
def submit_job(req: JobSubmit, db: Session = Depends(get_db)):
    job = create_job(db, current_user.id, req.job_type, req.payload)
    run_job.delay(str(job.id))
    return JobResponse(id=str(job.id), status=job.status, job_type=job.job_type)

@app.get("/jobs/{job_id}", response_model=JobResponse)
def job_status(job_id: str, db: Session = Depends(get_db)):
    try:
        jid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job_id")

    job = get_job(db, jid)
    if job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")

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

@app.get("/jobs", response_model=list[JobResponse])
def list_my_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
):
    jobs = list_jobs(db, current_user.id, limit=limit, offset=offset, status=status)

    out: list[JobResponse] = []
    for job in jobs:
        result = job.artifacts.output if job.artifacts and job.artifacts.output is not None else None
        out.append(
            JobResponse(
                id=str(job.id),
                status=job.status,
                job_type=job.job_type,
                result=result,
                error=job.error,
            )
        )
    return out


# Sprint shortcut: create tables automatically.
# Later we’ll replace this with Alembic migrations.
@app.on_event("startup")
def _create_tables():
    Base.metadata.create_all(bind=engine)
