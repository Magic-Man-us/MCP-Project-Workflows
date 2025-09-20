"""Tests for the workflow orchestrator."""

from __future__ import annotations

from pathlib import Path

from mcp_workflows.builder import WorkflowBuilder
from mcp_workflows.orchestrator import WorkflowOrchestrator
from mcp_workflows.spec import StepKind


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
