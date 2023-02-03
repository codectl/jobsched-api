from datetime import datetime

from src.models.job import JobStatus


def test_qsub_deserializer(qsub_job):
    job = qsub_job
    assert job.name == "STDIN"
    assert job.queue == "testq"
    assert job.submit_args == "-- /bin/sleep 1000"
    assert job.stdout_path == "/tmp/STDIN.o1"
    assert job.stderr_path == "/tmp/STDIN.e1"
    assert job.resources.cpu == 5
    assert job.resources.gpu == 2
    assert job.resources.node_count == 2
    assert job.resources.place == "pack"
    assert job.resources.walltime == "02:00:00"
    assert job.account == "pbs_account"
    assert job.project == "_pbs_project_default"
    assert job.interactive is False
    assert job.rerunable is True


def test_qstat_deserializer(qstat_job):
    job = qstat_job

    # qsub fields only
    assert job.name == "STDIN"
    assert job.queue == "workq"
    assert job.submit_args == "-X -I -l select=1:ncpus=24:mem=32gb -l walltime=24:00:00"
    assert job.stdout_path == "/home/testu/STDIN.o1"
    assert job.stderr_path == "/home/testu/STDIN.e1"
    assert job.resources.request.cpu == 24
    assert job.resources.request.node_count == 1
    assert job.resources.request.place == "free"
    assert job.resources.request.walltime == "24:00:00"
    assert job.account == "pbs_account"
    assert job.project == "_pbs_project_default"
    assert job.interactive is True
    assert job.rerunable is False

    # qstat fields
    assert job.owner == "testu"
    assert job.status == JobStatus.RUNNING
    assert job.server == "pbs01"
    assert job.comment == "Job run on Jan 01 at 00:00 on (cn01:ncpus=24:mem=33554432kb)"
    assert job.timeline.created_at == datetime(2023, 2, 3, 10, 41, 52)
