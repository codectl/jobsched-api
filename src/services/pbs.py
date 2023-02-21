import os

from shell import shell

from src.models.job import JobStat, JobSubmit
from src.services.sched import Sched


class PBS(Sched):

    def qstat(self, job_id=None, status=None) -> JobStat:
        data = self._exec(action="qstat", args=job_id)
        return JobStat(**data)

    def qsub(self, props: JobSubmit) -> str:
        return self._exec(action="qsub", args=props.to_qsub())

    def _exec(self, action, args):
        exe = os.path.join(self.env["PBS_EXEC"], "bin", action)
        cmd = " ".join((exe, args))
        return shell(command=cmd).output(raw=True)
