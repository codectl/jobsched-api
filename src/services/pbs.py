from src.models.job import JobSubmit
from src.services.sched import Sched


class PBS(Sched):
    def qstat(self, job_id=None, status=None):
        pass

    def qsub(self, props: JobSubmit):
        pass

    @staticmethod
    def _parse_qsub_props(props: JobSubmit):
        args = []
        if props.name is not None:
            args.append(("-N", props.name))
        if props.queue is not None:
            args.append(("-q", props.queue))
        if props.stdout_path is not None:
            args.append(("-o", props.stdout_path))
        if props.stderr_path is not None:
            args.append(("-e", props.stderr_path))
        if props.priority is not None:
            args.append(("-p", props.priority))
        if props.rerunable is not None:
            args.append(("-r", "y" if props.rerunable else "n"))
        if props.notify_on is not None:
            email_to = props.notify_on.to
            events = ""
            args.append(("-M", ", ".join(email_to)))
            if props.notify_on.on_started:
                events += "b"
            if props.notify_on.on_finished:
                events += "e"
            if props.notify_on.on_aborted:
                events += "a"
            if events:
                args.append(("-m", events))

        if props.account is not None:
            args.append(("-A", props.account))
        if props.project is not None:
            args.append(("-P", props.project))

        select = ""
        # if

    def _run_pbs_command(self, command: str):
        cmd = f"{self.exec_path} {self._parse_qsub_props()}"
