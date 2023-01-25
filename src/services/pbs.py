from src.models.job import Job
from src.services.sched import Sched


class PBS(Sched):

    def qstat(self, job_id=None, status=None):
        """Check for a job given job properties."""
        pass

    def qsub(self, props: Job):
        """Submit a job to the scheduler based on given job properties."""
        raise NotImplementedError
