from typing import Callable

import pyautogui


class RemoteController:
    """Handles the actual actions of the remote controller.

    Attributes
    ----------
    allowed_actions : dict
        The actions the remote controller may perform.

    """

    def __init__(self) -> None:
        """Instantiates the `RemoteController`."""
        self.allowed_actions = {
            "play": self._play_pause,
            "pause": self._play_pause,
            "forward": self._forward,
            "rewind": self._rewind,
        }

    def execute_action(self, action: str) -> None:
        """Execute the `action`.

        Parameters
        ----------
        action : str
            The action to perform.

        Raises
        ------
        ValueError
            When `action` is not an allowed action.
        """
        if action not in self.allowed_actions:
            raise ValueError(f"{action} is not a valid action.")
        self.allowed_actions[action]()

    def _focus(func: Callable) -> Callable:
        """Simple decorator to try to focus the screen before performing an action."""

        def wrapper(*args, **kwargs):
            cur_x, cur_y = pyautogui.position()
            # tiny relative move, then back to original position
            pyautogui.move(1, 1)
            pyautogui.moveTo(cur_x, cur_y)
            return func(*args, **kwargs)

        return wrapper

    @_focus
    def _play_pause(self) -> None:
        """Play or pause the video."""
        _, y = pyautogui.size()
        # Coordinates are quite arbitrary, just want to click somewhere
        # nothing is located.
        pyautogui.click(50, y / 2)

    @_focus
    def _forward(self) -> None:
        """Fast forward the video. Fast-forward behavior (number of seconds skipped)
        depends on the video player in use.
        """
        pyautogui.press("right")

    @_focus
    def _rewind(self) -> None:
        """Rewind the video. Rewind behavior (number of seconds skipped)
        depends on the video player in use.
        """
        pyautogui.press("left")
