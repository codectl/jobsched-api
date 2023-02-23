import pytest

from src.app import create_app


@pytest.fixture(scope="function")
def local_app():
    app = create_app(
        environ="testing",
        configs={
            "FLASK_RUN_HOST": "localhost",
            "FLASK_RUN_PORT": 5000,
            "APPLICATION_ROOT": "/test/v1",
        },
    )
    with app.app_context():
        yield app


class TestApp:
    def test_can_create_app(self, app):
        assert app is not None

    def test_root_path_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_swagger_apidocs_returns_200(self, client):
        response = client.get("/specs.json")
        assert response.status_code == 200

    def test_url_application_root_returns_200(self, local_app):
        client = local_app.test_client()

        response = client.get("/")
        assert response.status_code == 302

        response = client.get("/", follow_redirects=True)
        request = response.request
        assert response.status_code == 200
        assert request.path.rstrip("/") == "/test/v1"

        response = client.get("/test/v1/specs.json")
        assert response.status_code == 200

    def test_missing_path_throws_404(self, client):
        response = client.get("/404")
        assert response.status_code == 404
        assert response.json["code"] == 404
        assert "Not Found" in response.json["description"]
