import pytest

from src.services.pbs import PBS
from src.models.job import Job


@pytest.fixture(scope="class")
def pbs():
    return PBS


@pytest.fixture(scope="class")
def job():
    return Job(
        name="PBS job",
        queue="queue",
    )


class TestPBS:
    def test_qsub(self, pbs, job):
        job.dict(exclude_none=True)
