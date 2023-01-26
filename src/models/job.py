from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, FilePath, create_model, validator


class JobStatus(Enum):
    ARRAY_JOB = "B"
    EXIT = "E"
    FINISH = "F"
    HOLD = "H"
    MOVED = "M"
    QUEUE = "Q"
    RUNNING = "R"
    TRANSFER = "T"
    WAIT = "W"
    SUSPEND = "S"


class Job(BaseModel):
    job_id: Optional[str] = None
    name: str = Field(None, alias="Job_Name")
    owner: Optional[str] = Field(None, alias="Job_Owner")
    status: Optional[JobStatus] = Field(None, alias="job_state")
    queue: Optional[str] = None
    server: Optional[str] = None
    account: Optional[str] = Field(None, alias="Account_Name")
    project: Optional[str] = None
    created_at: Optional[datetime] = Field(None, alias="ctime")
    updated_at: Optional[datetime] = Field(None, alias="mtime")
    queued_at: Optional[datetime] = Field(None, alias="qtime")
    stdout_path: Optional[str] = Field(None, alias="Output_Path")
    stderr_path: Optional[str] = Field(None, alias="Error_Path")
    priority: Optional[int] = Field(None, alias="Priority")
    interactive: Optional[bool] = None
    rerunable: Optional[bool] = Field(None, alias="Rerunable")
    env: Optional[dict] = Field(None, alias="Variable_List")
    resources: Optional[create_model(
        "Resources",
        select=(str, ...),
        mem=(Optional[str], None),
        cpu=(Optional[int], Field(None, alias="ncpus")),
        gpu=(Optional[int], Field(None, alias="ngpus")),
        nodes=(Optional[int], Field(None, alias="nodect")),
        place=(Optional[str], None),
        walltime=(Optional[str], None),
    )] = Field(None, alias="Resource_List")

    @validator("created_at", "updated_at", "queued_at", pre=True)
    def parse_date(cls, value):
        return datetime.strptime(value, "%a %b %d %H:%M:%S %Y")
