from src.models.job import Job
from src.services.sched import Sched


class PBS(Sched):
    def qstat(self, job_id=None, status=None):
        pass

    def qsub(self, props: Job):
        pass
