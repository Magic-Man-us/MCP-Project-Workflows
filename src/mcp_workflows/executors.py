"""Execution strategies for workflow steps."""

from __future__ import annotations

from typing import Protocol

from .spec import StepRequest, StepResponse


class Executor(Protocol):
    """Protocol describing a component capable of running a workflow step."""

    def execute(self, request: StepRequest) -> StepResponse:
        """Run the step and return a response payload."""


class LLMExecutor:
    """Return canned responses for language model steps."""

    def execute(self, request: StepRequest) -> StepResponse:
        """Produce a deterministic response for the orchestrator."""

        message = f"{request.name} :: synthesized response"
        result = {"message": message, "echo": request.input}
        return StepResponse(status="ok", result=result, quality="good")


class ShellExecutor:
    """Placeholder shell executor."""

    def execute(self, request: StepRequest) -> StepResponse:  # pragma: no cover - stub
        raise NotImplementedError


class PythonExecutor:
    """Placeholder python executor."""

    def execute(self, request: StepRequest) -> StepResponse:  # pragma: no cover - stub
        raise NotImplementedError


__all__ = ["Executor", "LLMExecutor", "ShellExecutor", "PythonExecutor"]
