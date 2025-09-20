"""Observer hook definitions."""

from __future__ import annotations

from typing import Protocol

from .spec import StepRequest, StepResponse


class StepObserver(Protocol):
    """Observer interface receiving step lifecycle notifications."""

    def on_step_start(self, request: StepRequest) -> None:
        """Called before a step executes."""

    def on_step_finish(self, request: StepRequest, response: StepResponse) -> None:
        """Called after a step completes successfully."""

    def on_step_error(self, request: StepRequest, response: StepResponse) -> None:
        """Called when a step reports a failure."""
