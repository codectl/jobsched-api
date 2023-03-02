from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Extra, Field, root_validator, validator

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


class JobBaseModel(BaseModel, ABC, allow_population_by_field_name=True):
    @abstractmethod
    def parse_args(self) -> list[(str, Optional[str])]:
        raise NotImplementedError


class JobResources(JobBaseModel):
    node_count: Optional[int] = Field(None, alias="nodect")
    mem: Optional[str] = None
    cpu: Optional[int] = Field(None, alias="ncpus")
    gpu: Optional[int] = Field(None, alias="ngpus")
    select: Optional[str] = None
    place: Optional[str] = None
    walltime: Optional[str] = None

    def parse_args(self):
        args = []
        if self.node_count is not None:
            args.append(("-l", f"nodect={self.node_count}"))
        if self.cpu is not None:
            args.append(("-l", f"ncpus={self.cpu}"))
        if self.gpu is not None:
            args.append(("-l", f"ngpus={self.gpu}"))
        if self.mem is not None:
            args.append(("-l", f"mem={self.mem}"))
        if self.select is not None:
            args.append(("-l", f"select={self.select}"))
        if self.place is not None:
            args.append(("-l", f"place={self.place}"))
        if self.walltime is not None:
            args.append(("-l", f"walltime={self.walltime}"))
        return args


class JobResourcesType(BaseModel):
    request: Optional[JobResources] = Field(None, alias="Resource_List")
    used: Optional[JobResources] = Field(None, alias="resources_used")


class JobTimeline(BaseModel):
    created_at: Optional[datetime] = Field(None, alias="ctime")
    updated_at: Optional[datetime] = Field(None, alias="mtime")
    queued_at: Optional[datetime] = Field(None, alias="qtime")
    ready_at: Optional[datetime] = Field(None, alias="etime")

    @validator("*", pre=True)
    def parse_date(cls, value):
        return datetime.strptime(value, "%a %b %d %H:%M:%S %Y")


class JobPaths(JobBaseModel):
    stdout: Optional[str] = Field(None, alias="Output_Path")
    stderr: Optional[str] = Field(None, alias="Error_Path")
    join_mode: Optional[str] = Field(None, alias="Join_Path")
    shell: Optional[str] = Field(None, alias="Shell_Path_List")

    def parse_args(self):
        args = []
        if self.stdout is not None:
            args.append(("-o", self.stdout))
        if self.stderr is not None:
            args.append(("-e", self.stderr))
        if self.shell is not None:
            args.append(("-S", self.shell))
        if self.join_mode is None and self.stderr is None:
            # redirect stderr to stdout if mode is not specified
            args.append(("-j", "oe"))
        elif self.join_mode is not None:
            args.append(("-j", self.join_mode))
        return args


class JobFlags(JobBaseModel):
    interactive: Optional[bool] = None
    rerunable: Optional[bool] = Field(None, alias="Rerunable")
    copy_env: Optional[bool] = None
    forward_X11: Optional[bool] = Field(None, alias="forward_x11_port")
    hold: Optional[bool] = None
    array: Optional[bool] = None

    def parse_args(self):
        args = []
        if self.interactive:
            args.append(("-I",))
        if self.rerunable is not None:
            args.append(("-r", "y" if self.rerunable else "n"))
        if self.copy_env is not None:
            args.append(("-V",))
        if self.forward_X11:
            args.append(("-X",))
        if self.hold:
            args.append(("-h",))
        return args


class JobNotification(JobBaseModel):
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

    def parse_args(self):
        args, events = [], ""
        if self.to is not None:
            args.append(("-M", ", ".join(self.to)))
        if self.on_started:
            events += "b"
        if self.on_finished:
            events += "e"
        if self.on_aborted:
            events += "a"
        if events:
            args.append(("-m", events))
        return args


class JobExtra(JobBaseModel):
    class Config:
        extra = Extra.allow

    priority: Optional[int] = Field(None, alias="Priority")
    account: Optional[str] = Field(None, alias="Account_Name")
    project: Optional[str] = None
    paths: Optional[JobPaths] = None
    flags: Optional[JobFlags] = None
    notify_on: Optional[JobNotification] = None
    array_range: Optional[str] = Field(None, alias="array_indices_submitted")
    env: Optional[dict] = Field(None, alias="Variable_List")

    def parse_args(self):
        args = []
        if self.priority is not None:
            args.append(("-p", str(self.priority)))
        if self.account is not None:
            args.append(("-A", self.account))
        if self.project is not None:
            args.append(("-P", self.project))
        if self.paths is not None:
            args += self.paths.parse_args()
        if self.notify_on is not None:
            args += self.notify_on.parse_args()
        if self.array_range is not None:
            args.append(("-J", self.array_range))
        if self.env is not None:
            values = (f"{k}={v}" for k, v in self.env.items())
            args.append(("-v", ", ".join(values)))
        # extra attrs
        vrs = vars(self).items()
        extras = ("=".join((k, str(v))) for k, v in vrs if k not in self.__fields__)
        if extras:
            args.append(("-W", ", ".join(sorted(extras))))
        return args


class Job(JobBaseModel, ABC):
    """
    The generic attributes of a job.
    For PBS job documentations, see at https://bit.ly/3WG0Mmg.
    """

    name: Optional[str] = Field(None, alias="Job_Name")
    queue: Optional[str] = None
    submit_args: Optional[str] = Field(None, alias="Submit_arguments")
    resources: Optional[JobResources] = None
    extra: Optional[JobExtra] = None


class JobStat(Job, JobExtra):
    job_id: Optional[str] = None
    owner: Optional[str] = Field(None, alias="Job_Owner")
    status: Optional[JobStatus] = Field(None, alias="job_state")
    server: Optional[str] = None
    resources: Optional[JobResourcesType] = None
    comment: Optional[str] = None
    timeline: Optional[JobTimeline] = None
    hold_type: Optional[str] = Field(None, alias="Hold_Types")
    extra: Optional[dict] = None

    @root_validator(pre=True)
    def unflatten(cls, values: dict[str, Any]) -> dict[str, Any]:
        return unflatten(model=cls, values=values)

    @root_validator(pre=True)
    def extra_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        values["extra"] = build_extra(cls, deepcopy(values))
        return values


class JobSubmit(Job):
    def parse_args(self):
        args = []
        if self.name is not None:
            args.append(("-N", self.name))
        if self.queue is not None:
            args.append(("-q", self.queue))
        if self.resources is not None:
            args += self.resources.parse_args()
        if self.extra is not None:
            args += self.extra.parse_args()
            # make flags come first
            if self.extra.flags is not None:
                args = self.extra.flags.parse_args() + args
        if self.submit_args is not None:
            args.append(("--", self.submit_args.lstrip("- ")))
        return args

    def to_qsub(self):
        args = self.parse_args()
        return " ".join((" " if len(arg) > 1 else "").join(arg) for arg in args)
