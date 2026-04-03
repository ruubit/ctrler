import pytest

from ctrler.remote_controller import RemoteController


@pytest.fixture
def remote_controller(monkeypatch):
    def mock_pyautogui(*args, **kwargs):
        return

    monkeypatch.setattr("pyautogui.click", mock_pyautogui)
    monkeypatch.setattr("pyautogui.press", mock_pyautogui)
    return RemoteController()


@pytest.mark.parametrize("action", ["play", "pause", "rewind", "forward"])
def test_execute_allowed_action(action, remote_controller):
    remote_controller.execute_action(action)


def test_execute_not_allowed_action(remote_controller):
    with pytest.raises(ValueError):
        remote_controller.execute_action("foo")
