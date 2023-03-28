import pytest

from src.services.pbs import PBS
from src.models.job import JobStat, JobSubmit


@pytest.fixture(scope="class")
def pbs():
    return PBS(
        env={
            "EXEC_PATH": "/opt/pbs",
            "HOME_PATH": "/var/spool/pbs",
            "SERVER": "pbs00",
        }
    )


@pytest.fixture(scope="class")
def job_stat(qstat_data):
    return JobStat(**qstat_data)


@pytest.fixture(scope="class")
def job_submit(qsub_data):
    return JobSubmit(**qsub_data)


class TestPBSService:
    def test_qstat(self, pbs, qstat_data, mock_shell):
        mock_shell.configure_mock(**{"output.return_value": qstat_data})
        job = pbs.qstat(job_id="123")
        submit_args = "-X -I -l select=1:ncpus=24:mem=32gb -l walltime=24:00:00"
        assert job.name == "STDIN"
        assert job.queue == "workq"
        assert job.submit_args == submit_args
        assert job.paths.stdout == "/home/testu/STDIN.o1"
        assert job.paths.stderr == "/home/testu/STDIN.e1"
        assert job.paths.join_mode == "n"
        assert job.account == "pbs_account"
        assert job.project == "_pbs_project_default"

    def test_qsub(self, pbs, job_submit):
        pbs.qsub(props=job_submit)
