"""Tests for the workflow builder."""

from __future__ import annotations

from pathlib import Path

from mcp_workflows.builder import WorkflowBuilder
from mcp_workflows.spec import StepKind


def test_builder_produces_spec_and_yaml(tmp_path: Path) -> None:
    """Builder compiles to a spec and emits deterministic YAML."""

    output_path = tmp_path / "demo.yaml"
    builder = (
        WorkflowBuilder.start()
        .with_goal("Ship a demo workflow")
        .memory("memory.md")
        .register_task("notes", text="Remember to check inputs")
        .add_step(
            "Gather",
            kind=StepKind.LLM,
            doc="Collect requirements",
            uses=["notes"],
            input_template="{{ context }}",
            config={"temperature": 0.2},
        )
        .end()
    )
    spec = builder.compile()
    assert spec.goal == "Ship a demo workflow"
    assert spec.memory_file == "memory.md"
    assert len(spec.tasks) == 1
    assert len(spec.steps) == 1

    builder.emit_yaml(output_path)
    contents_first = output_path.read_text(encoding="utf-8")
    builder.emit_yaml(output_path)
    contents_second = output_path.read_text(encoding="utf-8")
    assert contents_first == contents_second
