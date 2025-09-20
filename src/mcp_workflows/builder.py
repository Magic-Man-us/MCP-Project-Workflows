"""Workflow builder utilities."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml

from .spec import Branch, StepKind, StepSpec, TaskSpec, WorkflowSpec


class WorkflowBuilder:
    """Incrementally assemble a :class:`WorkflowSpec`."""

    def __init__(self) -> None:
        self._goal: str | None = None
        self._memory_file: str | None = None
        self._tasks: dict[str, TaskSpec] = {}
        self._steps: list[StepSpec] = []

    @classmethod
    def start(cls) -> WorkflowBuilder:
        """Create a new builder instance."""
        return cls()

    def with_goal(self, goal: str) -> WorkflowBuilder:
        """Set the primary goal for the workflow."""
        self._goal = goal
        return self

    def memory(self, path: str | Path) -> WorkflowBuilder:
        """Configure the memory file path used during execution."""
        self._memory_file = str(path)
        return self

    def register_task(
        self,
        task_id: str,
        *,
        file: str | Path | None = None,
        text: str | None = None,
    ) -> WorkflowBuilder:
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
    ) -> WorkflowBuilder:
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

    def end(self) -> WorkflowBuilder:
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
        yaml_text = yaml.safe_dump(
            data,
            sort_keys=sort_keys,
            default_flow_style=False,
            allow_unicode=True,
        )
        output_path.write_text(yaml_text, encoding="utf-8")
        return output_path

    @staticmethod
    def _coerce_branch(branch: Branch | dict[str, Any]) -> Branch:
        """Normalize branch definitions into :class:`Branch` instances."""
        if isinstance(branch, Branch):
            return branch
        return Branch(**branch)
