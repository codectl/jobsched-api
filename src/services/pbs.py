from __future__ import annotations

import os

from shell import shell

from src.models.job import JobStat, JobSubmit
from src.services.sched import Sched


class PBS(Sched):
    def qstat(self, job_id=None, status=None) -> None | JobStat:
        args = " ".join(("-xf", "-F json", job_id))
        data = self._exec(action="qstat", args=args)
        if not data:
            return None
        job_data = next(data["Jobs"].values())
        return JobStat(**job_data)

    def qsub(self, props: JobSubmit) -> str:
        return self._exec(action="qsub", args=props.to_qsub())

    def _exec(self, action, args):
        exe = os.path.join(self.env["EXEC_PATH"], "bin", action)
        cmd = " ".join((exe, args))
        return shell(command=cmd).output(raw=True)
