from typing import Any, Literal
from pydantic import BaseModel, Field

JobType = Literal["test_sleep", "validate_payload"]

class JobSubmit(BaseModel):
    job_type: JobType
    payload: dict[str, Any] = Field(default_factory=dict)

class JobResponse(BaseModel):
    id: str
    status: str
    job_type: str
    result: dict | None = None
    error: str | None = None
