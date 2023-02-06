from abc import ABC
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
    class Config:
        allow_population_by_field_name = True

    mem: Optional[str] = None
    cpu: Optional[int] = Field(None, alias="ncpus")
    gpu: Optional[int] = Field(None, alias="ngpus")
    node_count: Optional[int] = Field(None, alias="nodect")
    place: Optional[str] = None
    walltime: Optional[str] = None


class _JobResourcesType(BaseModel):
    class Config:
        allow_population_by_field_name = True

    request: Optional[_JobResources] = Field(None, alias="Resource_List")
    used: Optional[_JobResources] = Field(None, alias="resources_used")


class _JobTimeline(BaseModel):
    created_at: Optional[datetime] = Field(None, alias="ctime")
    updated_at: Optional[datetime] = Field(None, alias="mtime")
    queued_at: Optional[datetime] = Field(None, alias="qtime")
    ready_at: Optional[datetime] = Field(None, alias="etime")

    @validator("*", pre=True)
    def parse_date(cls, value):
        return datetime.strptime(value, "%a %b %d %H:%M:%S %Y")


class _JobNotification(BaseModel):
    class Config:
        allow_population_by_field_name = True

    to: Optional[list[str]] = Field(None, alias="Mail_Users")
    on_started: Optional[bool] = None
    on_finished: Optional[bool] = None
    on_aborted: Optional[bool] = None
    events: Optional[str] = Field(None, alias="Mail_Points")

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


class _JobFlags(BaseModel):
    interactive: Optional[bool] = None
    rerunable: Optional[bool] = Field(None, alias="Rerunable")
    forward_X11: Optional[bool] = Field(None, alias="forward_x11_port")

    class Config:
        allow_population_by_field_name = True


class Job(BaseModel, ABC):
    """
    The attributes of a job.
    For PBS job documentations, see at https://bit.ly/3WG0Mmg.
    """

    class Config:
        allow_population_by_field_name = True

    name: Optional[str] = Field(None, alias="Job_Name")
    queue: Optional[str] = None
    submit_args: Optional[str] = Field(None, alias="Submit_arguments")
    stdout_path: Optional[str] = Field(None, alias="Output_Path")
    stderr_path: Optional[str] = Field(None, alias="Error_Path")
    resources: Optional[_JobResources] = None
    account: Optional[str] = Field(None, alias="Account_Name")
    project: Optional[str] = None
    priority: Optional[int] = Field(None, alias="Priority")
    flags: Optional[_JobFlags] = None
    env: Optional[dict] = Field(None, alias="Variable_List")
    notify_on: Optional[_JobNotification] = None


class JobStat(Job):
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


class JobSubmit(Job):
    def to_qsub(self) -> str:
        args: list[(str, str)] = []
        if self.name is not None:
            args.append(("-N", self.name))
        if self.queue is not None:
            args.append(("-q", self.queue))
        if self.stdout_path is not None:
            args.append(("-o", self.stdout_path))
        if self.stderr_path is not None:
            args.append(("-e", self.stderr_path))
        if self.priority is not None:
            args.append(("-p", str(self.priority)))
        if self.account is not None:
            args.append(("-A", self.account))
        if self.project is not None:
            args.append(("-P", self.project))

        # flags
        if self.flags.interactive is not None:
            args.append(("-I", ""))
        if self.flags.rerunable is not None:
            args.append(("-r", "y" if self.flags.rerunable else "n"))
        if self.flags.forward_X11 is not None:
            args.append(("-X", ""))

        # email notification
        if self.notify_on is not None:
            email_to = self.notify_on.to
            events = ""
            args.append(("-M", ", ".join(email_to)))
            if self.notify_on.on_started:
                events += "b"
            if self.notify_on.on_finished:
                events += "e"
            if self.notify_on.on_aborted:
                events += "a"
            if events:
                args.append(("-m", events))

        # resources
        select = []
        if self.resources.node_count is not None:
            select.append((str(self.resources.node_count), ""))
        if self.resources.cpu is not None:
            select.append(("ncpus", str(self.resources.cpu)))
        if self.resources.gpu is not None:
            select.append(("ngpus", str(self.resources.gpu)))
        if self.resources.mem is not None:
            select.append(("mem", self.resources.mem))
        print(args)
        print(select)
        args.append(("-l", ":".join((("=" if s[1] else "").join(s) for s in select))))

        if self.resources.place is not None:
            args.append(("-l", f"place={self.resources.place}"))
        if self.resources.walltime is not None:
            args.append(("-l", f"walltime={self.resources.walltime}"))

        return " ".join((" " if arg[1] else "").join(arg) for arg in args)
