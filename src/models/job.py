from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, create_model, root_validator, validator


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
    """
    The attributes of a job.
    For PBS job documentations, see at https://bit.ly/3WG0Mmg.
    """
    job_id: Optional[str] = None
    name: str = Field(None, alias="Job_Name")
    owner: Optional[str] = Field(None, alias="Job_Owner")
    status: Optional[JobStatus] = Field(None, alias="job_state")
    queue: Optional[str] = None
    server: Optional[str] = None
    submit_args: Optional[str] = Field(None, alias="Submit_arguments")
    stdout_path: Optional[str] = Field(None, alias="Output_Path")
    stderr_path: Optional[str] = Field(None, alias="Error_Path")
    resources: Optional[create_model(
        "Resources",
        select=(str, ...),
        mem=(Optional[str], None),
        cpu=(Optional[int], Field(None, alias="ncpus")),
        gpu=(Optional[int], Field(None, alias="ngpus")),
        node_count=(Optional[int], Field(None, alias="nodect")),
        place=(Optional[str], None),
        walltime=(Optional[str], None),
    )] = Field(None, alias="Resource_List")
    comment: Optional[str] = None
    account: Optional[str] = Field(None, alias="Account_Name")
    project: Optional[str] = None
    created_at: Optional[datetime] = Field(None, alias="ctime")
    updated_at: Optional[datetime] = Field(None, alias="mtime")
    queued_at: Optional[datetime] = Field(None, alias="qtime")
    ready_at: Optional[datetime] = Field(None, alias="etime")
    priority: Optional[int] = Field(None, alias="Priority")
    interactive: Optional[bool] = None
    rerunable: Optional[bool] = Field(None, alias="Rerunable")
    env: Optional[dict] = Field(None, alias="Variable_List")
    mail_to: Optional[list] = Field(None, alias="Mail_Users")
    extra: Optional[dict] = None

    class Config:
        allow_population_by_field_name = True

    @root_validator(pre=True)
    def extra_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        extra: dict[str, Any] = {}
        fields = {f.alias for f in cls.__fields__.values() if f.alias != "extra"}
        for k, v in values.items():
            if k not in fields:
                extra[k] = v
        values["extra"] = extra
        return values

    @validator("created_at", "updated_at", "queued_at", "ready_at", pre=True)
    def parse_date(cls, value):
        return datetime.strptime(value, "%a %b %d %H:%M:%S %Y")