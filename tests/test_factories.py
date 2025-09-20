"""Tests for the executor factory and service container."""

from __future__ import annotations

import pytest

from mcp_workflows.executors import LLMExecutor
from mcp_workflows.factories import ExecutorFactory
from mcp_workflows.spec import StepKind, StepRequest, StepResponse


class SampleExecutor:
    """Simple executor counting the number of invocations."""

    def __init__(self) -> None:
        self.calls = 0

    def execute(self, request: StepRequest) -> StepResponse:
        self.calls += 1
        return StepResponse(status="ok", result={"message": request.name})


def test_register_singleton_reuses_instance() -> None:
    """Singleton registration should reuse the same executor object."""

    factory = ExecutorFactory()
    factory.register_singleton(StepKind.SHELL, lambda _: SampleExecutor())
    first = factory.create(StepKind.SHELL)
    second = factory.create(StepKind.SHELL)
    assert first is second


def test_register_factory_creates_new_instances() -> None:
    """Factories should produce a new executor for each request."""

    factory = ExecutorFactory()
    factory.register_factory(StepKind.SHELL, lambda _: SampleExecutor())
    first = factory.create(StepKind.SHELL)
    second = factory.create(StepKind.SHELL)
    assert first is not second


def test_register_instance_returns_provided_executor() -> None:
    """register_instance should return the same executor that was supplied."""

    factory = ExecutorFactory()
    executor = SampleExecutor()
    factory.register_instance(StepKind.PYTHON, executor)
    assert factory.create(StepKind.PYTHON) is executor


def test_default_factory_provides_llm_executor() -> None:
    """The default factory seeds a canned LLM executor implementation."""

    factory = ExecutorFactory.default()
    executor = factory.create(StepKind.LLM)
    assert isinstance(executor, LLMExecutor)
    response = executor.execute(
        StepRequest(
            step_id=1,
            name="Default",
            kind=StepKind.LLM,
            correlation_id="demo",
            input="",
            memory_text="",
            config={},
        )
    )
    assert response.status == "ok"


def test_missing_registration_raises_value_error() -> None:
    """Requesting an unknown executor should raise a :class:`ValueError`."""

    factory = ExecutorFactory()
    with pytest.raises(ValueError):
        factory.create(StepKind.SHELL)
