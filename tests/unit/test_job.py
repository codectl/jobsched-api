from datetime import datetime

from src.models.job import JobStatus


def test_qsub_deserializer(qsub_job):
    job = qsub_job
    assert job.name == "STDIN"
    assert job.queue == "testq"
    assert job.submit_args == "-- /bin/sleep 1000"
    assert job.resources.mem == "10gb"
    assert job.resources.cpu == 5
    assert job.resources.gpu == 2
    assert job.resources.node_count == 2
    assert job.resources.place == "pack"
    assert job.resources.walltime == "02:00:00"
    assert job.paths.stdout == "/tmp/STDIN.o1"
    assert job.paths.stderr == "/tmp/STDIN.e1"
    assert job.paths.join_mode == "oe"
    assert job.extra.account == "pbs_account"
    assert job.extra.project == "_pbs_project_default"
    assert job.extra.flags.interactive is True
    assert job.extra.flags.rerunable is True
    assert job.extra.flags.forward_X11 is True
    assert job.extra.flags.copy_env is False
    assert job.extra.env == {"HOME": "/home/user", "SHELL": "/bin/bash"}
    assert job.extra.block is True


def test_qstat_deserializer(qstat_job):
    job = qstat_job

    # common fields
    assert job.name == "STDIN"
    assert job.queue == "workq"
    assert job.submit_args == "-X -I -l select=1:ncpus=24:mem=32gb -l walltime=24:00:00"
    assert job.paths.stdout == "/home/testu/STDIN.o1"
    assert job.paths.stderr == "/home/testu/STDIN.e1"
    assert job.paths.join_mode == "n"
    assert job.account == "pbs_account"
    assert job.project == "_pbs_project_default"
    assert job.flags.interactive is True
    assert job.flags.rerunable is False
    assert job.flags.forward_X11 is True

    # qstat fields
    assert job.owner == "testu"
    assert job.status == JobStatus.RUNNING
    assert job.server == "pbs01"
    assert job.resources.request.mem == "32gb"
    assert job.resources.request.cpu == 24
    assert job.resources.request.node_count == 1
    assert job.resources.request.place == "free"
    assert job.resources.request.walltime == "24:00:00"
    assert job.resources.used.mem == "32gb"
    assert job.resources.used.cpu == 24
    assert job.resources.used.walltime == "00:02:00"
    assert job.comment == "Job run on Jan 01 at 00:00 on (cn01:ncpus=24:mem=33554432kb)"
    assert job.timeline.created_at == datetime(2023, 2, 3, 10, 41, 52)
    assert job.timeline.updated_at == datetime(2023, 2, 3, 10, 41, 52)
    assert job.timeline.queued_at == datetime(2023, 2, 3, 10, 41, 53)
    assert job.timeline.ready_at == datetime(2023, 2, 3, 10, 41, 53)
    assert job.hold_type == "n"
    assert isinstance(job.extra, dict) is True
    assert isinstance(job.env, dict) is True


def test_job_qsub_clause(qsub_job):
    qsub = "-I -r y -X -N STDIN -q testq " \
           "-l nodect=2 -l ncpus=5 -l ngpus=2 -l mem=10gb " \
           "-l place=pack -l walltime=02:00:00 " \
           "-o /tmp/STDIN.o1 -e /tmp/STDIN.e1 -j oe " \
           "-A pbs_account -P _pbs_project_default -p 0 " \
           "-M testu@email.com -m be " \
           "-v HOME=/home/user, SHELL=/bin/bash " \
           "-W block=True, umask=33"
    assert qsub_job.to_qsub() == qsub
