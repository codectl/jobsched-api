from base64 import b64encode

import pytest


@pytest.fixture()
def auth(app, mocker):
    mocker.patch("src.api.auth.load_user", return_value=None)
    mocker.patch("src.services.auth.AuthSvc.authenticate", return_value=True)
    return {"Authorization": f"Basic {b64encode(b'user:pass').decode()}"}


class TestPBSQsubPOST:
    def test_unauthorized_request_throws_401(self, client):
        response = client.post("/pbs/qsub", headers={})
        assert response.status_code == 401

    def test_valid_job_returns_200(self, client, auth, qsub_job):
        response = client.post("/pbs/qsub", headers=auth, json=qsub_job.dict())
        print(response.json)
        assert response.status_code == 200
        assert response.text == ""
        assert response.json == ["file.txt"]
