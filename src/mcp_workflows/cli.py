"""Command line helpers for workflow utilities."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .builder import WorkflowBuilder
from .orchestrator import WorkflowOrchestrator

DEFAULT_OUTPUT = Path("workflows/demo.yaml")
DEFAULT_MEMORY = Path("memory.md")
DEFAULT_GOAL = "Demonstrate workflow builder output"


def create_demo_builder(goal: str, memory_file: Path = DEFAULT_MEMORY) -> WorkflowBuilder:
    """Construct the demo workflow builder with shared configuration."""

    return (
        WorkflowBuilder.start()
        .with_goal(goal)
        .memory(memory_file)
        .register_task("normalize", file=Path("tasks/normalize.md"))
        .register_task("quality_gate", file=Path("tasks/quality_gate.md"))
        .add_step(
            "Demo Plan",
            doc="Collect requirements and outline the work to perform.",
            uses=["normalize", "quality_gate"],
        )
        .end()
    )


def build_demo_workflow(
    goal: str,
    output_path: Path = DEFAULT_OUTPUT,
    memory_file: Path = DEFAULT_MEMORY,
) -> Path:
    """Generate a simple demo workflow YAML file."""

    builder = create_demo_builder(goal, memory_file)
    builder.emit_yaml(output_path)
    return output_path


def run_demo_workflow(goal: str, memory_file: Path = DEFAULT_MEMORY) -> None:
    """Run the demo workflow using the canned orchestrator."""

    builder = create_demo_builder(goal, memory_file)
    spec = builder.compile()
    WorkflowOrchestrator(spec).run()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments for the demo builder."""

    parser = argparse.ArgumentParser(description="Emit a demo workflow YAML file.")
    parser.add_argument(
        "--goal",
        default=DEFAULT_GOAL,
        help="Goal statement stored in the generated workflow",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_OUTPUT),
        help="Destination path for the generated YAML file",
    )
    parser.add_argument(
        "--memory",
        default=str(DEFAULT_MEMORY),
        help="Path to the shared memory file",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Execute the demo workflow after emitting YAML",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point used by ``mcp_workflows.main``."""

    args = parse_args(argv)
    output_path = Path(args.out)
    memory_path = Path(args.memory)
    build_demo_workflow(goal=args.goal, output_path=output_path, memory_file=memory_path)
    print(f"Workflow written to {output_path}")
    if args.run:
        run_demo_workflow(goal=args.goal, memory_file=memory_path)
        print(f"Workflow executed; memory updated at {memory_path}")
    return 0


__all__ = [
    "main",
    "build_demo_workflow",
    "create_demo_builder",
    "parse_args",
    "run_demo_workflow",
]
