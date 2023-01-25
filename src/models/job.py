import datetime
from aenum import NamedConstant
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


@dataclass
class _Status:
    name: str
    description: str


class JobStatus(NamedConstant):
    E = _Status("exiting", "job is exiting after having run")
    H = _Status("held", "job is	held")
    Q = _Status("queued", "job is queued, eligible to run or be routed")
    R = _Status("running", "job is running")
    T = _Status("transferring", "job is	being moved to new location")
    W = _Status("waiting", "job is waiting for its execution time")
    S = _Status("suspended", "job is suspended")


class Job(BaseModel):
    job_id: Optional[str] = None
    name: str
    owner: str
    status: JobStatus
    queue: str
    server: str
    account: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    queued_at: Optional[datetime.datetime] = None
    stderr_path: Path
    stdout_path: Path
    priority: int = 0
    interactive: Optional[bool] = None
