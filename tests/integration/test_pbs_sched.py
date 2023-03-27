import json
from base64 import b64encode

import pytest

from src.services.pbs import PBS


@pytest.fixture(scope="class", autouse=True)
def pbs(class_mocker):
    class_mocker.patch(
        "src.api.pbs.PBS",
        return_value=PBS(
            env={
                "EXEC_PATH": "/opt/pbs/2022",
                "HOME_PATH": "/opt/pbs/2022/var/spool",
                "SERVER": "pbs00",
            }
        ),
    )


@pytest.fixture()
def auth(app, mocker):
    mocker.patch("src.api.auth.load_user", return_value=None)
    mocker.patch("src.services.auth.AuthSvc.authenticate", return_value=True)
    return {"Authorization": f"Basic {b64encode(b'user:pass').decode()}"}


class TestPBSQstatGET:
    def test_valid_job_id_returns_200(
        self, client, auth, qstat_data, qstat_job, mock_shell
    ):
        mock_shell.configure_mock(**{"output.return_value": qstat_data})
        response = client.get("/pbs/qstat/100.pbs00", headers=auth)
        assert response.status_code == 200
        assert response.json == json.loads(qstat_job.json())

    def test_unauthorized_request_throws_401(self, client):
        response = client.get("/pbs/qstat/100.pbs00", headers={})
        assert response.status_code == 401
        assert response.json == {"code": 401, "description": "Unauthorized"}

    def test_not_found_job_throws_404(self, client, auth, mock_shell):
        mock_shell.configure_mock(**{"output.return_value": None})
        response = client.get("/pbs/qstat/00.pbs00", headers=auth)
        assert response.status_code == 404
        assert response.json["code"] == 404
        assert response.json["description"] == "Not Found: job '00.pbs00' not found"

    def test_disallowed_method_throws_405(self, client):
        response = client.post("/pbs/qstat/100.pbs00")
        assert response.status_code == 405
        assert response.json == {"code": 405, "description": "Method Not Allowed"}


class TestPBSQsubPOST:
    def test_valid_job_returns_200(self, client, auth, qsub_job, mock_shell):
        job_id = "100.pbs00"
        mock_shell.configure_mock(**{"output.return_value": job_id})
        response = client.post("/pbs/qsub", headers=auth, json=qsub_job.dict())
        assert response.status_code == 200
        assert response.json == {"job_id": job_id}

    def test__throws_400(self, client, auth, qsub_job, mock_shell):
        response = client.post("/pbs/qsub", headers=auth, json={"resources": "?"})
        assert response.status_code == 400
        assert response.json["code"] == 400
        assert "Bad Request" in response.json["description"]

    def test_unauthorized_request_throws_401(self, client):
        response = client.post("/pbs/qsub", headers={})
        assert response.status_code == 401
        assert response.json == {"code": 401, "description": "Unauthorized"}

    def test_disallowed_method_throws_405(self, client):
        response = client.get("/pbs/qsub")
        assert response.status_code == 405
        assert response.json == {"code": 405, "description": "Method Not Allowed"}
