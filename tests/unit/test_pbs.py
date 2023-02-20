import pytest

from src.services.pbs import PBS
from src.models.job import JobStat, JobSubmit


@pytest.fixture(scope="class")
def pbs():
    return PBS(env={
        "PBS_EXEC": "/opt/pbs/2022",
        "PBS_HOME": "/opt/pbs/2022/var/spool",
        "PBS_SERVER": "pbs00",
    })


@pytest.fixture(scope="class")
def job_stat(qstat_data):
    return JobStat(**qstat_data)


@pytest.fixture(scope="class")
def job_submit(qsub_data):
    return JobSubmit(**qsub_data)


@pytest.fixture(scope="class", autouse=True)
def mock_shell(class_mocker):
    mock = class_mocker.Mock()
    return class_mocker.patch("src.services.pbs.shell", return_value=mock).return_value


class TestPBSService:

    def test_qstat(self, pbs, qstat_data, mock_shell):
        mock_shell.configure_mock(**{"output.return_value": qstat_data})
        job = pbs.qstat(job_id="123")
        assert False

    def test_qsub(self, pbs, job_submit):
        job_submit.dict()
