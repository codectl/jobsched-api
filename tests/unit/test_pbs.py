import pytest

from src.services.pbs import PBS
from src.models.job import JobStat, JobSubmit


@pytest.fixture(scope="class")
def pbs():
    return PBS


@pytest.fixture(scope="class")
def job_submit():
    return JobSubmit(
        name="PBS job",
        queue="testq",
    )


class TestPBS:
    def test_qsub(self, pbs, job_submit):
        job_submit.dict()

    def test_qstat(self, pbs, job_submit):
        job_submit.dict()
