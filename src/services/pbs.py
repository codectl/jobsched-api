from src.models.job import JobSubmit
from src.services.sched import Sched


class PBS(Sched):
    def qstat(self, job_id=None, status=None):
        pass

    def qsub(self, props: JobSubmit):
        pass

    def _run_pbs_command(self, command: str):
        cmd = f"{self.exec_path} {self._parse_qsub_props()}"
