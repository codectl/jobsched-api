from copy import deepcopy
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, root_validator, validator
from pydantic.utils import lenient_issubclass


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
    select: str
    mem: Optional[str] = None
    cpu: Optional[int] = Field(None, alias="ncpus")
    gpu: Optional[int] = Field(None, alias="ngpus")
    node_count: Optional[int] = Field(None, alias="nodect")
    place: Optional[str] = None
    walltime: Optional[str] = None


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
    _events: Optional[str] = Field(None, alias="Mail_Points")

    @validator("to", pre=True)
    def parse_to(cls, value):
        return value.split(",")

    # @validator("_events", pre=True)
    # def parse_events(cls, value):
    #     return value

    # class Config:
    #     underscore_attrs_are_private = True

    # @validator("on_finished", pre=True, allow_reuse=True)
    # def parse_on_started(cls, value):
    #     return "e" in value
    #
    # @validator("on_aborted", pre=True, allow_reuse=True)
    # def parse_on_started(cls, value):
    #     return "a" in value


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
    resources: Optional[_JobResources] = Field(None, alias="Resource_List")
    comment: Optional[str] = None
    account: Optional[str] = Field(None, alias="Account_Name")
    project: Optional[str] = None
    priority: Optional[int] = Field(None, alias="Priority")
    interactive: Optional[bool] = None
    rerunable: Optional[bool] = Field(None, alias="Rerunable")
    env: Optional[dict] = Field(None, alias="Variable_List")
    timeline: Optional[_JobTimeline] = None
    notify_on: Optional[_JobNotification] = None
    extra: Optional[dict] = None

    class Config:
        allow_population_by_field_name = True

    @root_validator(pre=True)
    def unflatten(cls, values: dict[str, Any]) -> dict[str, Any]:
        complex_fields = [
            field for field in cls.__fields__.values()
            if lenient_issubclass(field.type_, BaseModel)
        ]

        for field in complex_fields:
            subset = {k: v for k, v in values.items() if k != field.alias}
            values.setdefault(field.alias, subset)

        return values

    @root_validator(pre=True)
    def extra_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        values["extra"] = cls.extras(cls, deepcopy(values))
        return values

    @classmethod
    def extras(cls, model, values):
        for field in model.__fields__.values():
            if lenient_issubclass(field.type_, BaseModel):
                cls.extras(field.type_, values)

            if field.alias in values:
                values.pop(field.alias)

        return values
