"""Workflow template definitions for structured workflow creation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

import yaml

from .spec import BaseTask, StepKind, StepSpec, TaskSpec


@dataclass
class WorkflowTemplate:
    """Template defining the structure and contents of a workflow."""

    name: str

    # Folder structure: path -> content or None (for directories)
    structure: Dict[str, str | None] = field(default_factory=dict)

    # Goal statement for the workflow
    goal: str = "Write production-ready code for the specified task"

    # Memory file path
    memory_file: str = "memory.md"

    # Steps definitions using proper models
    steps: list[StepSpec] = field(default_factory=lambda: [
        StepSpec(
            id=1,
            name="Gather Requirements",
            kind=StepKind.LLM,
            doc="Collect and analyze all requirements for the coding task",
            uses=("requirements",)
        ),
        StepSpec(
            id=2,
            name="Design Solution",
            kind=StepKind.LLM,
            doc="Plan the architecture and approach for implementation",
            uses=("requirements", "design")
        ),
        StepSpec(
            id=3,
            name="Implement Code",
            kind=StepKind.LLM,
            doc="Write the actual code following the design plan",
            uses=("design", "implement")
        ),
        StepSpec(
            id=4,
            name="Test and Review",
            kind=StepKind.LLM,
            doc="Test the code, review for quality, and suggest improvements",
            uses=("implement", "test")
        ),
    ])

    # BaseTask definitions using proper models
    base_tasks: list[BaseTask] = field(default_factory=lambda: [
        BaseTask(
            name="requirements",
            objective="Gather and clarify all requirements for the coding task",
            description="Collect functional requirements, constraints, input/output specifications, and understand success criteria",
            substeps=(
                "Identify functional requirements",
                "Identify constraints and edge cases",
                "Clarify input/output specifications",
                "Note dependencies and prerequisites",
            ),
            instructions="Analyze the task requirements thoroughly. Consider all possible inputs, edge cases, and success criteria.",
            expected_output="Complete requirements specification ready for design phase",
            success_criteria=(
                "All functional requirements documented",
                "Constraints and edge cases identified",
                "Input/output specifications clear",
                "Dependencies documented",
            ),
        ),
        BaseTask(
            name="design",
            objective="Design the solution architecture and approach",
            description="Plan the solution structure, algorithms, data flow, interfaces, and error handling approach",
            prerequisites=("Requirements gathered",),
            substeps=(
                "Design solution structure and architecture",
                "Plan algorithms and data flow",
                "Define interfaces and modules",
                "Consider error handling approach",
            ),
            instructions="Create a comprehensive design that addresses all requirements while considering maintainability, scalability, and error conditions.",
            expected_output="Complete design specification ready for implementation",
            success_criteria=(
                "Solution structure defined",
                "Algorithms and data flow planned",
                "Interfaces designed",
                "Error handling considered",
            ),
        ),
        BaseTask(
            name="implement",
            objective="Implement production-ready code following best practices",
            description="Write clean, readable, well-structured code that follows language conventions and handles errors properly",
            prerequisites=("Design completed",),
            substeps=(
                "Write clean, readable code",
                "Follow language best practices",
                "Add meaningful comments",
                "Handle exceptions properly",
            ),
            sites_to_visit=(
                "https://peps.python.org/pep-0008/",  # For Python
                "https://docs.oracle.com/javase/tutorial/java/nutsandbolts/index.html",  # For Java
                "https://developer.mozilla.org/en-US/docs/Web/JavaScript",  # For JS
            ),
            instructions="Implement the code following the design specifications. Add comprehensive error handling, logging, and documentation.",
            expected_output="Production-ready code implementation",
            success_criteria=(
                "Code is clean and readable",
                "Follows language best practices",
                "Errors are properly handled",
                "Code is well-documented",
            ),
        ),
        BaseTask(
            name="test",
            objective="Test code thoroughly and ensure quality",
            description="Write unit tests, test edge cases, error conditions, and verify the implementation meets all requirements",
            prerequisites=("Code implemented",),
            substeps=(
                "Write unit tests for key functions",
                "Test edge cases and error conditions",
                "Review code for bugs and optimization",
                "Suggest improvements",
            ),
            instructions="Create comprehensive tests covering normal operation, edge cases, and error conditions. Verify all requirements are met.",
            expected_output="Thoroughly tested code with identified issues addressed",
            success_criteria=(
                "Unit tests written for key functions",
                "Edge cases and errors tested",
                "Code reviewed for quality",
                "Improvement suggestions provided",
            ),
        ),
    ])

    # Derived TaskSpec instances (computed from base_tasks)
    @property
    def tasks(self) -> list[TaskSpec]:
        """Convert base_tasks to TaskSpec instances."""
        return [base_task.to_task_spec() for base_task in self.base_tasks]

    def __post_init__(self) -> None:
        """Initialize default structure if not provided."""
        if not self.structure:
            self._init_default_structure()

    def _init_default_structure(self) -> None:
        """Initialize the default folder structure."""
        self.structure = {
            # Root config
            "workflow.yaml": self._generate_workflow_yaml(),
            "README.md": self._generate_readme(),

            # Memory file
            "memory.md": "# Workflow Memory\n\nSession memory for workflow execution.",

            # Memory directory (for additional memory files)
            "memory/": None,

            # Tasks directory (for custom task files)
            "tasks/": None,

            # Config directory
            "config/": None,
            "config/steps.yaml": self._generate_steps_config(),

            # Logs directory
            "logs/": None,

            # Results/output directory
            "results/": None,
        }

    def _generate_workflow_yaml(self) -> str:
        """Generate the main workflow YAML content."""

        data = {
            "goal": self.goal,
            "memory_file": self.memory_file,
            "tasks": [task.as_dict() for task in self.tasks],
            "steps": [step.as_dict() for step in self.steps]
        }
        return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)

    def _generate_readme(self) -> str:
        """Generate README content for the workflow."""
        return f"""# {self.name}

This workflow was generated automatically using MCP Workflows.

## Structure
- `workflow.yaml` - Main workflow configuration
- `config/` - Additional configuration files
- `tasks/` - Custom task definitions
- `memory/` - Workflow memory and state
- `results/` - Workflow outputs and artifacts
- `logs/` - Execution logs

## Running the Workflow

To run this workflow:
```bash
python -m mcp_workflows.cli run {self.name}
```

## Contents
{chr(10).join(f"- {path}" for path in sorted(self.structure.keys()) if path)}
"""

    def _generate_steps_config(self) -> str:
        """Generate detailed steps configuration."""

        steps_data = {
            "description": "Detailed step configuration",
            "steps": [step.as_dict() for step in self.steps]
        }
        return yaml.safe_dump(steps_data, sort_keys=False, allow_unicode=True)


# Predefined templates use default BaseTask instances
CODE_WORKFLOW_TEMPLATE = WorkflowTemplate(
    name="code_workflow",
    goal="Write production-ready code for the specified task",
    memory_file="memory.md",
)


def get_template(template_name: str) -> WorkflowTemplate:
    """Get a template by name."""
    templates = {
        "code": CODE_WORKFLOW_TEMPLATE,
        "code_workflow": CODE_WORKFLOW_TEMPLATE,
    }

    if template_name not in templates:
        raise ValueError(f"Unknown template: {template_name}. Available: {list(templates.keys())}")

    return templates[template_name]


def create_workflow_from_template(template: WorkflowTemplate, base_path: Path) -> Path:
    """Create a complete workflow folder structure from a template."""
    folder_path = base_path / template.name
    folder_path.mkdir(parents=True, exist_ok=True)

    for path_str, content in template.structure.items():
        path = folder_path / path_str

        if content is None:
            # It's a directory
            path.mkdir(parents=True, exist_ok=True)
        else:
            # It's a file
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    return folder_path


__all__ = [
    "CODE_WORKFLOW_TEMPLATE",
    "WorkflowTemplate",
    "create_workflow_from_template",
    "get_template",
]
