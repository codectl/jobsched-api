from copy import deepcopy
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, root_validator, validator

from src.utils import build_extra, unflatten


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


class _JobResources(BaseModel):
    mem: Optional[str] = None
    cpu: Optional[int] = Field(None, alias="ncpus")
    gpu: Optional[int] = Field(None, alias="ngpus")
    node_count: Optional[int] = Field(None, alias="nodect")
    place: Optional[str] = None
    walltime: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


class _JobResourcesType(BaseModel):
    request: Optional[_JobResources] = Field(None, alias="Resource_List")
    used: Optional[_JobResources] = Field(None, alias="resources_used")

    class Config:
        allow_population_by_field_name = True


class _JobTimeline(BaseModel):
    created_at: Optional[datetime] = Field(None, alias="ctime")
    updated_at: Optional[datetime] = Field(None, alias="mtime")
    queued_at: Optional[datetime] = Field(None, alias="qtime")
    ready_at: Optional[datetime] = Field(None, alias="etime")

    @validator("*", pre=True)
    def parse_date(cls, value):
        return datetime.strptime(value, "%a %b %d %H:%M:%S %Y")


class _JobNotification(BaseModel):
    to: Optional[list[str]] = Field(None, alias="Mail_Users")
    on_started: Optional[bool] = None
    on_finished: Optional[bool] = None
    on_aborted: Optional[bool] = None
    events: Optional[str] = Field(None, alias="Mail_Points")

    class Config:
        allow_population_by_field_name = True

    @validator("to", pre=True)
    def parse_to(cls, value):
        return value.split(",") if isinstance(value, str) else value

    @root_validator
    def parse_events(cls, values: dict[str, Any]) -> dict[str, Any]:
        events = values.pop("events") or ""
        if "b" in events:
            values["on_started"] = True
        if "e" in events:
            values["on_finished"] = True
        if "a" in events:
            values["on_aborted"] = True

        return values


class JobSubmit(BaseModel):
    """
    The attributes of a job submission.
    For PBS job documentations, see at https://bit.ly/3WG0Mmg.
    """

    name: Optional[str] = Field(None, alias="Job_Name")
    queue: Optional[str] = None
    submit_args: Optional[str] = Field(None, alias="Submit_arguments")
    stdout_path: Optional[str] = Field(None, alias="Output_Path")
    stderr_path: Optional[str] = Field(None, alias="Error_Path")
    resources: Optional[_JobResources] = None
    account: Optional[str] = Field(None, alias="Account_Name")
    project: Optional[str] = None
    priority: Optional[int] = Field(None, alias="Priority")
    interactive: Optional[bool] = None
    rerunable: Optional[bool] = Field(None, alias="Rerunable")
    env: Optional[dict] = Field(None, alias="Variable_List")
    notify_on: Optional[_JobNotification] = None

    class Config:
        allow_population_by_field_name = True


class JobStat(JobSubmit):
    job_id: Optional[str] = None
    owner: Optional[str] = Field(None, alias="Job_Owner")
    status: Optional[JobStatus] = Field(None, alias="job_state")
    server: Optional[str] = None
    resources: Optional[_JobResourcesType] = None
    comment: Optional[str] = None
    timeline: Optional[_JobTimeline] = None
    extra: Optional[dict] = None

    @root_validator(pre=True)
    def unflatten(cls, values: dict[str, Any]) -> dict[str, Any]:
        return unflatten(model=cls, values=values)

    @root_validator(pre=True)
    def extra_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        values["extra"] = build_extra(cls, deepcopy(values))
        return values
