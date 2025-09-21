"""Command line helpers for workflow utilities."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from .builder import WorkflowBuilder
from .orchestrator import WorkflowOrchestrator
from .tasks import DESIGN_MD, IMPLEMENTATION_MD, REQUIREMENTS_MD, TESTING_MD
from .templates import create_workflow_from_template

DEFAULT_GOAL = "Write production-ready code for the specified task"


def run_code_workflow(workflow_name: str, goal: str, workflow_folder: Path) -> None:
    """Run a code workflow using the canned orchestrator."""

    memory_file = workflow_folder / "memory.md"
    builder = create_code_workflow_builder(workflow_name)
    builder._goal = goal  # Override the default goal
    builder._memory_file = str(memory_file)
    spec = builder.compile()
    WorkflowOrchestrator(spec).run()


def create_code_workflow_builder(workflow_name: str) -> WorkflowBuilder:
    """Create a builder for a multi-step code writing workflow."""

    return (
        WorkflowBuilder.start()
        .with_goal("Write production-ready code for the specified task")
        .memory("memory.md")  # Relative to workflow folder
        .register_task("requirements", text=REQUIREMENTS_MD)
        .register_task("design", text=DESIGN_MD)
        .register_task("implement", text=IMPLEMENTATION_MD)
        .register_task("test", text=TESTING_MD)
        .add_step(
            "Gather Requirements",
            doc="Collect and analyze all requirements for the coding task",
            uses=["requirements"],
        )
        .add_step(
            "Design Solution",
            doc="Plan the architecture and approach for implementation",
            uses=["requirements", "design"],
        )
        .add_step(
            "Implement Code",
            doc="Write the actual code following the design plan",
            uses=["design", "implement"],
        )
        .add_step(
            "Test and Review",
            doc="Test the code, review for quality, and suggest improvements",
            uses=["implement", "test"],
        )
    )


def build_code_workflow(workflow_name: str) -> Path:
    """Create a complete code workflow in its own folder using templates."""

    from .templates import WorkflowTemplate

    template = WorkflowTemplate(workflow_name)
    return create_workflow_from_template(template, Path("workflows"))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments for the workflow builder."""

    parser = argparse.ArgumentParser(description="Create and run code writing workflows.")
    parser.add_argument(
        "--goal",
        default=DEFAULT_GOAL,
        help="Goal statement for the workflow",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Execute the workflow after creation",
    )
    parser.add_argument(
        "name",
        help="Name of the workflow to create in workflows/NAME/ folder",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point used by ``mcp_workflows.main``."""

    args = parse_args(argv)

    # Create code workflow
    workflow_folder = build_code_workflow(args.name)
    workflow_yaml = workflow_folder / "workflow.yaml"
    memory_file = workflow_folder / "memory.md"

    print(f"Code writing workflow '{args.name}' created in: {workflow_folder}")
    print(f"  - Workflow YAML: {workflow_yaml}")
    print(f"  - Memory file: {memory_file}")

    if args.run:
        run_code_workflow(args.name, args.goal, workflow_folder)
        print(f"Workflow executed; memory updated at {memory_file}")

    return 0


__all__ = [
    "build_code_workflow",
    "create_code_workflow_builder",
    "main",
    "parse_args",
    "run_code_workflow",
]
