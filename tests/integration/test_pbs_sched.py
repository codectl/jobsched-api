import json
from base64 import b64encode

import pytest

from src.services.pbs import PBS


@pytest.fixture(scope="class", autouse=True)
def pbs(class_mocker):
    class_mocker.patch("src.api.pbs.PBS", return_value=PBS(env={
        "PBS_EXEC": "/opt/pbs/2022",
        "PBS_HOME": "/opt/pbs/2022/var/spool",
        "PBS_SERVER": "pbs00",
    }))


@pytest.fixture()
def auth(app, mocker):
    mocker.patch("src.api.auth.load_user", return_value=None)
    mocker.patch("src.services.auth.AuthSvc.authenticate", return_value=True)
    return {"Authorization": f"Basic {b64encode(b'user:pass').decode()}"}


class TestPBSQstatGET:
    def test_valid_job_id_returns_200(self, client, auth, qstat_data, qstat_job,
                                      mock_shell):
        mock_shell.configure_mock(**{"output.return_value": qstat_data})
        response = client.get("/pbs/qstat/100.pbs00", headers=auth)
        assert response.status_code == 200
        assert response.json == json.loads(qstat_job.json())

    def test_unauthorized_request_throws_401(self, client):
        response = client.get("/pbs/qstat/100.pbs00", headers={})
        assert response.status_code == 401

    def test_not_found_job_throws_404(self, client, auth, mock_shell):
        mock_shell.configure_mock(**{"output.return_value": None})
        response = client.get("/pbs/qstat/?.pbs00", headers=auth)
        assert response.status_code == 404

    def test_disallowed_method_throws_405(self, client):
        response = client.post("/pbs/qstat/100.pbs00")
        assert response.status_code == 405


class TestPBSQsubPOST:
    def test_valid_job_returns_200(self, client, auth, qsub_job, mock_shell):
        job_id = "100.pbs00"
        mock_shell.configure_mock(**{"output.return_value": job_id})
        response = client.post("/pbs/qsub", headers=auth, json=qsub_job.dict())
        assert response.status_code == 200
        assert response.json == {"job_id": job_id}

    def test_unauthorized_request_throws_401(self, client):
        response = client.post("/pbs/qsub", headers={})
        assert response.status_code == 401

    def test_disallowed_method_throws_405(self, client):
        response = client.get("/pbs/qsub")
        assert response.status_code == 405
