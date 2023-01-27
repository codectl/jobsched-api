import abc
from pathlib import Path
from typing import Optional, Union

from src.models.job import Job, JobStatus


class Sched(abc.ABC):
    def __init__(
            self,
            exec_path: Optional[Path] = None,
            server: Optional[str] = None,
    ):
        self.exec_path = exec_path
        self.server = server

    @abc.abstractmethod
    def qstat(
        self,
        job_id: str = None,
        status: Union[None, JobStatus, list[JobStatus]] = None,
    ) -> Union[Job, list[Job]]:
        """
        Check for a job given job properties.
        job_id: the id of the job; if provided, a single job is returned
        status: the status of the job
        """
        raise NotImplementedError

    @abc.abstractmethod
    def qsub(self, props: Job) -> str:
        """Submit a job to the scheduler based on given job properties."""
        raise NotImplementedError
