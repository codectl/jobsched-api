from base64 import b64encode

import pytest

from src.services.pbs import PBS


@pytest.fixture(scope="class")
def svc():
    return PBS


@pytest.fixture()
def auth(app, mocker):
    mocker.patch("src.api.auth.load_user", return_value=None)
    mocker.patch("src.services.auth.AuthSvc.authenticate", return_value=True)
    return {"Authorization": f"Basic {b64encode(b'user:pass').decode()}"}


class TestPBSQsubPOST:
    def test_unauthorized_request_throws_401(self, client):
        response = client.post("/pbs/qsub", headers={})
        assert response.status_code == 401
