"""Workflow builder utilities."""

from __future__ import annotations

from json import dumps
from pathlib import Path
from typing import Any, Iterable

from .spec import Branch, StepKind, StepSpec, TaskSpec, WorkflowSpec


class WorkflowBuilder:
    """Incrementally assemble a :class:`WorkflowSpec`."""

    def __init__(self) -> None:
        self._goal: str | None = None
        self._memory_file: str | None = None
        self._tasks: dict[str, TaskSpec] = {}
        self._steps: list[StepSpec] = []

    @classmethod
    def start(cls) -> "WorkflowBuilder":
        """Create a new builder instance."""

        return cls()

    def with_goal(self, goal: str) -> "WorkflowBuilder":
        """Set the primary goal for the workflow."""

        self._goal = goal
        return self

    def memory(self, path: str | Path) -> "WorkflowBuilder":
        """Configure the memory file path used during execution."""

        self._memory_file = str(path)
        return self

    def register_task(
        self,
        task_id: str,
        *,
        file: str | Path | None = None,
        text: str | None = None,
    ) -> "WorkflowBuilder":
        """Register a reusable task document."""

        if task_id in self._tasks:
            msg = f"Task '{task_id}' is already registered."
            raise ValueError(msg)
        task = TaskSpec(id=task_id, file=str(file) if file else None, text=text)
        self._tasks[task_id] = task
        return self

    def add_step(
        self,
        name: str,
        *,
        kind: StepKind = StepKind.LLM,
        doc: str = "",
        uses: Iterable[str] | None = None,
        input_template: str | None = None,
        config: dict[str, Any] | None = None,
        branches: Iterable[Branch | dict[str, Any]] | None = None,
        next_step: int | None = None,
    ) -> "WorkflowBuilder":
        """Append a new step definition to the workflow."""

        step_id = len(self._steps) + 1
        uses_list = list(uses) if uses else []
        for task_id in uses_list:
            if task_id not in self._tasks:
                msg = f"Step '{name}' references unknown task '{task_id}'."
                raise ValueError(msg)
        branch_models: list[Branch] = []
        if branches:
            for branch in branches:
                branch_models.append(self._coerce_branch(branch))
        step = StepSpec(
            id=step_id,
            name=name,
            kind=kind,
            doc=doc,
            uses=uses_list,
            input_template=input_template,
            config=config or {},
            branches=branch_models,
            next_step=next_step,
        )
        self._steps.append(step)
        return self

    def end(self) -> "WorkflowBuilder":
        """Finalize step additions (no-op placeholder for fluent API)."""

        return self

    def compile(self) -> WorkflowSpec:
        """Produce the immutable :class:`WorkflowSpec`."""

        if not self._goal:
            msg = "Workflow goal must be provided before compilation."
            raise ValueError(msg)
        if not self._memory_file:
            msg = "Memory file must be configured before compilation."
            raise ValueError(msg)
        return WorkflowSpec(
            goal=self._goal,
            memory_file=self._memory_file,
            tasks=list(self._tasks.values()),
            steps=list(self._steps),
        )

    def emit_yaml(self, path: str | Path, *, sort_keys: bool = False) -> Path:
        """Compile the workflow and write it as YAML to ``path``."""

        spec = self.compile()
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = spec.as_dict()
        if sort_keys:
            serialized = _dump_yaml(_sort_mapping(data))
        else:
            serialized = _dump_yaml(data)
        yaml_text = f"{serialized}\n"
        output_path.write_text(yaml_text, encoding="utf-8")
        return output_path

    @staticmethod
    def _coerce_branch(branch: Branch | dict[str, Any]) -> Branch:
        """Normalize branch definitions into :class:`Branch` instances."""

        if isinstance(branch, Branch):
            return branch
        return Branch(**branch)


def _dump_yaml(value: Any, indent: int = 0) -> str:
    """Serialize data to a minimal YAML representation."""

    if isinstance(value, dict):
        lines: list[str] = []
        for key, item in value.items():
            prefix = " " * indent
            if _is_scalar(item):
                lines.append(f"{prefix}{key}: {_format_scalar(item)}")
            else:
                lines.append(f"{prefix}{key}:")
                lines.append(_dump_yaml(item, indent + 2))
        return "\n".join(lines)
    if isinstance(value, list):
        lines = []
        for item in value:
            prefix = " " * indent
            if _is_scalar(item):
                lines.append(f"{prefix}- {_format_scalar(item)}")
            else:
                lines.append(f"{prefix}-")
                lines.append(_dump_yaml(item, indent + 2))
        return "\n".join(lines)
    return f"{' ' * indent}{_format_scalar(value)}"


def _format_scalar(value: Any) -> str:
    """Render scalar values in YAML-compatible form."""

    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    return dumps(value)


def _is_scalar(value: Any) -> bool:
    """Determine if a value is representable as a scalar."""

    return not isinstance(value, (dict, list))


def _sort_mapping(value: Any) -> Any:
    """Recursively sort mapping keys for deterministic serialization."""

    if isinstance(value, dict):
        return {key: _sort_mapping(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [_sort_mapping(item) for item in value]
    return value
