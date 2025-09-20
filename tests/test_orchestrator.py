"""Tests for the workflow orchestrator."""

from __future__ import annotations

from pathlib import Path

from mcp_workflows.builder import WorkflowBuilder
from mcp_workflows.factories import ExecutorFactory
from mcp_workflows.orchestrator import WorkflowOrchestrator
from mcp_workflows.spec import StepKind, StepRequest, StepResponse


class RecordingExecutor:
    """Test double capturing received step requests."""

    def __init__(self) -> None:
        self.requests: list[StepRequest] = []

    def execute(self, request: StepRequest) -> StepResponse:
        self.requests.append(request)
        return StepResponse(status="ok", result={"message": "recorded"})


def test_orchestrator_runs_and_writes_memory(tmp_path: Path) -> None:
    """Running the orchestrator appends a summary line to memory."""

    memory_path = tmp_path / "memory.md"
    builder = (
        WorkflowBuilder.start()
        .with_goal("Exercise orchestrator")
        .memory(memory_path)
        .register_task("notes", text="Remember to check output")
        .add_step("Demo", kind=StepKind.LLM, doc="Demo step")
        .end()
    )
    spec = builder.compile()
    orchestrator = WorkflowOrchestrator(spec)
    responses = orchestrator.run()
    assert len(responses) == 1
    assert memory_path.exists()
    memory_text = memory_path.read_text(encoding="utf-8")
    assert "Demo" in memory_text


def test_orchestrator_respects_explicit_executor_mapping(tmp_path: Path) -> None:
    """A provided executor dictionary overrides default registrations."""

    memory_path = tmp_path / "memory.md"
    builder = (
        WorkflowBuilder.start()
        .with_goal("Override executor")
        .memory(memory_path)
        .register_task("notes", text="Remember to check output")
        .add_step("Demo", kind=StepKind.LLM, doc="Demo step")
        .end()
    )
    spec = builder.compile()
    recording = RecordingExecutor()
    orchestrator = WorkflowOrchestrator(spec, executors={StepKind.LLM: recording})
    orchestrator.run()
    assert len(recording.requests) == 1


def test_orchestrator_uses_executor_factory_for_new_kinds(tmp_path: Path) -> None:
    """Factory integration allows registering executors for additional step kinds."""

    memory_path = tmp_path / "memory.md"
    builder = (
        WorkflowBuilder.start()
        .with_goal("Use shell executor")
        .memory(memory_path)
        .register_task("notes", text="Remember to check output")
        .add_step("Shell", kind=StepKind.SHELL, doc="Shell step")
        .end()
    )
    spec = builder.compile()
    recording = RecordingExecutor()
    factory = ExecutorFactory()
    factory.register_instance(StepKind.SHELL, recording)
    orchestrator = WorkflowOrchestrator(spec, executor_factory=factory)
    orchestrator.run()
    assert len(recording.requests) == 1
