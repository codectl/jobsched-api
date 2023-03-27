from __future__ import annotations

import json
import os

from shell import CommandError, shell

from src.models.job import JobStat, JobSubmit
from src.services.sched import Sched


class PBS(Sched):
    def qstat(self, job_id=None, status=None) -> None | JobStat:
        args = " ".join(("-xf", "-F json", job_id))
        data = self._exec(action="qstat", args=args)
        if not data:
            return None
        job_data = next(iter(json.loads(data)["Jobs"].values()))
        return JobStat(**job_data)

    def qsub(self, props: JobSubmit) -> str:
        return self._exec(action="qsub", args=props.to_qsub())

    def _exec(self, action, args):
        exe = os.path.join(self.env["EXEC_PATH"], "bin", action)
        cmd = " ".join((exe, args))
        sh = shell(command=cmd).run()
        if sh.code > 0:
            raise CommandError(sh.errors(raw=True))
        return sh.output(raw=True)
