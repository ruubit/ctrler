import pytest
from fastapi.testclient import TestClient

from ctrler.app import RemoteControllerApp


@pytest.fixture()
def remote_controller_app(monkeypatch):
    def mock_token_method(*args, **kwargs):
        return "test"

    monkeypatch.setattr(
        RemoteControllerApp, "_generate_session_token", mock_token_method
    )
    app = RemoteControllerApp(local_ip="foo.bar.baz")
    return app


@pytest.fixture
def test_client(remote_controller_app):
    fast_api_app = remote_controller_app._create_app()
    test_client = TestClient(fast_api_app)
    return test_client


def test_generate_service_url(remote_controller_app):
    assert remote_controller_app.service_url == "http://foo.bar.baz:8000#token=test"


@pytest.mark.parametrize("action", ["play", "pause", "rewind", "forward"])
def test_allowed_action(test_client, action):
    response = test_client.post(
        "/api/action",
        json={"action": action},
        headers={"Content-type": "application/json", "Authorization": "Bearer test"},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "success", "action": action}


def test_not_allowed_action(test_client):
    response = test_client.post(
        "/api/action",
        json={"action": "foo"},
        headers={"Content-type": "application/json", "Authorization": "Bearer test"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "foo is not a valid action."


@pytest.mark.parametrize(
    "action",
    ["play", "foo"],  # test for both allowed and not allowed actions
)
def test_action_rejected_no_authorization(test_client, action):
    response = test_client.post(
        "/api/action",
        json={"action": action},
        headers={
            "Content-type": "application/json",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.parametrize(
    "action",
    ["pause", "bar"],  # same, test for allowed and not allowed actions
)
def test_action_rejected_wrong_token(test_client, action):
    response = test_client.post(
        "/api/action",
        json={"action": action},
        headers={"Content-type": "application/json", "Authorization": "Bearer wrong"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authorized to control the remote."


def test_exception_in_execute_action(test_client, monkeypatch):
    def click_execution_failed(*args, **kwargs):
        raise Exception("Simulated pyautogui error")

    monkeypatch.setattr("pyautogui.click", click_execution_failed)
    response = test_client.post(
        "/api/action",
        json={"action": "play"},
        headers={"Content-type": "application/json", "Authorization": "Bearer test"},
    )
    assert response.status_code == 500
    assert "Executing action play failed" in response.json()["detail"]
