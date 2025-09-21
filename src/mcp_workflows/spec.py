"""Workflow specification contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal


class StepKind(str, Enum):
    """Supported execution strategies for workflow steps."""

    LLM = "llm"
    SHELL = "shell"
    PYTHON = "python"


@dataclass(frozen=True, slots=True)
class Branch:
    """Conditional jump instruction evaluated after a step completes."""

    when: str
    goto: int

    def as_dict(self) -> dict[str, Any]:
        """Serialize the branch for persistence."""

        return {"when": self.when, "goto": self.goto}


@dataclass(frozen=True, slots=True)
class BaseTask:
    """Base task definition with structured metadata for single-responsibility workflows."""

    name: str
    objective: str  # The single purpose/responsibility
    description: str  # Detailed explanation

    # Additional context and resources
    sites_to_visit: tuple[str, ...] = field(default_factory=tuple)
    substeps: tuple[str, ...] = field(default_factory=tuple)
    prerequisites: tuple[str, ...] = field(default_factory=tuple)

    # Execution details
    instructions: str = ""
    expected_output: str = ""
    success_criteria: tuple[str, ...] = field(default_factory=tuple)

    def to_task_spec(self, task_dir: str = "tasks") -> TaskSpec:
        """Convert to a TaskSpec that can be used in workflows."""
        task_content = self._generate_task_content()
        return TaskSpec(id=self.name, text=task_content)

    def _generate_task_content(self) -> str:
        """Generate the complete task content for this base task."""
        content_parts = [
            f"# {self.name}",
            "## Objective",
            f"{self.objective}",
            "",
            "## Description",
            f"{self.description}",
        ]

        if self.prerequisites:
            content_parts.extend([
                "",
                "## Prerequisites",
                *[f"- {prereq}" for prereq in self.prerequisites]
            ])

        if self.sites_to_visit:
            content_parts.extend([
                "",
                "## Resources",
                *[f"- {site}" for site in self.sites_to_visit]
            ])

        if self.substeps:
            content_parts.extend([
                "",
                "## Substeps",
                *[f"- {step}" for step in self.substeps]
            ])

        content_parts.extend([
            "",
            "## Instructions",
            f"{self.instructions}",
        ])

        if self.expected_output:
            content_parts.extend([
                "",
                "## Expected Output",
                f"{self.expected_output}"
            ])

        if self.success_criteria:
            content_parts.extend([
                "",
                "## Success Criteria",
                *[f"- {criteria}" for criteria in self.success_criteria]
            ])

        return "\n".join(content_parts)

    def __post_init__(self) -> None:
        # Convert lists to tuples for immutability
        object.__setattr__(self, "sites_to_visit", tuple(self.sites_to_visit))
        object.__setattr__(self, "substeps", tuple(self.substeps))
        object.__setattr__(self, "prerequisites", tuple(self.prerequisites))
        object.__setattr__(self, "success_criteria", tuple(self.success_criteria))


@dataclass(frozen=True, slots=True)
class TaskSpec:
    """Reusable document that can be referenced by workflow steps."""

    id: str
    file: str | None = None
    text: str | None = None

    def __post_init__(self) -> None:
        if not self.file and not self.text:
            msg = "TaskSpec requires a file or text source."
            raise ValueError(msg)

    def as_dict(self) -> dict[str, Any]:
        """Serialize the task for persistence."""

        payload: dict[str, Any] = {"id": self.id}
        if self.file is not None:
            payload["file"] = self.file
        if self.text is not None:
            payload["text"] = self.text
        return payload


@dataclass(frozen=True, slots=True)
class StepSpec:
    """Single executable unit in a workflow."""

    id: int
    name: str
    kind: StepKind
    doc: str = ""
    uses: tuple[str, ...] = field(default_factory=tuple)
    input_template: str | None = None
    config: dict[str, Any] = field(default_factory=dict)
    branches: tuple[Branch, ...] = field(default_factory=tuple)
    next_step: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "uses", tuple(self.uses))
        object.__setattr__(self, "branches", tuple(self.branches))
        object.__setattr__(self, "config", dict(self.config))

    def as_dict(self) -> dict[str, Any]:
        """Serialize the step for persistence."""

        payload: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "kind": self.kind.value,
            "doc": self.doc,
        }
        if self.uses:
            payload["uses"] = list(self.uses)
        if self.input_template is not None:
            payload["input"] = self.input_template
        if self.config:
            payload["config"] = dict(self.config)
        if self.branches:
            payload["branches"] = [branch.as_dict() for branch in self.branches]
        if self.next_step is not None:
            payload["next"] = self.next_step
        return payload


@dataclass(frozen=True, slots=True)
class WorkflowSpec:
    """Top-level contract describing a full workflow."""

    goal: str
    memory_file: str
    tasks: tuple[TaskSpec, ...] = field(default_factory=tuple)
    steps: tuple[StepSpec, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "tasks", tuple(self.tasks))
        object.__setattr__(self, "steps", tuple(self.steps))
        task_ids = {task.id for task in self.tasks}
        if len(task_ids) != len(self.tasks):
            msg = "WorkflowSpec tasks must have unique identifiers."
            raise ValueError(msg)
        step_ids = {step.id for step in self.steps}
        if len(step_ids) != len(self.steps):
            msg = "WorkflowSpec steps must have unique identifiers."
            raise ValueError(msg)

    def as_dict(self) -> dict[str, Any]:
        """Serialize the workflow for persistence."""

        return {
            "goal": self.goal,
            "memory_file": self.memory_file,
            "tasks": [task.as_dict() for task in self.tasks],
            "steps": [step.as_dict() for step in self.steps],
        }


@dataclass(frozen=True, slots=True)
class StepRequest:
    """Data sent to an executor for performing a workflow step."""

    step_id: int
    name: str
    kind: StepKind
    correlation_id: str
    input: Any
    memory_text: str
    config: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class StepResponse:
    """Result payload returned by an executor."""

    status: Literal["ok", "retry", "fail"]
    result: Any | None = None
    quality: str | None = None
    artifacts: tuple[str, ...] | None = None
    next_step: int | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        if self.artifacts is not None:
            object.__setattr__(self, "artifacts", tuple(self.artifacts))
