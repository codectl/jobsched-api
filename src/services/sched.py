import abc
from typing import Optional, Union

from src.models.job import JobStat, JobSubmit, JobStatus


class Sched(abc.ABC):
    def __init__(
        self,
        server: Optional[str] = None,
        env: Optional[dict] = None,
    ):
        self.server = server
        self.env = env

    @abc.abstractmethod
    def qstat(
        self,
        job_id: str = None,
        status: Union[None, JobStatus, list[JobStatus]] = None,
    ) -> Union[JobStat, list[JobStat]]:
        """
        Check for a job given job properties.
        job_id: the id of the job; if provided, a single job is returned
        status: the status of the job
        """
        raise NotImplementedError

    @abc.abstractmethod
    def qsub(self, props: JobSubmit) -> str:
        """Submit a job to the scheduler based on given job properties."""
        raise NotImplementedError
