import os

from shell import shell

from src.models.job import JobSubmit
from src.services.sched import Sched


class PBS(Sched):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bin = os.path.join(self.env["PBS_EXEC"], "bin")

    def qstat(self, job_id=None, status=None) -> dict:
        exe = os.path.join(self._bin, "qstat")
        cmd = " ".join((exe, job_id))
        return shell(command=cmd).output(raw=True)

    def qsub(self, props: JobSubmit) -> None:
        exe = os.path.join(self._bin, "qsub")
        cmd = " ".join((exe, props.to_qsub()))
        shell(command=cmd)
