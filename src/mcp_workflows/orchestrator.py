"""Workflow orchestration primitives."""

from __future__ import annotations

from pathlib import Path

from .executors import Executor, LLMExecutor
from .factories import ExecutorFactory
from .hooks import StepObserver
from .spec import StepKind, StepRequest, StepResponse, WorkflowSpec


class WorkflowOrchestrator:
    """Drive workflow execution using registered executors."""

    def __init__(
        self,
        spec: WorkflowSpec,
        *,
        observer: StepObserver | None = None,
        executors: dict[StepKind, Executor] | None = None,
        executor_factory: ExecutorFactory | None = None,
    ) -> None:
        self.spec = spec
        self.observer = observer
        factory = executor_factory or ExecutorFactory.default()
        if executors:
            for kind, executor in executors.items():
                factory.register_instance(kind, executor, override=True)
        if not factory.is_registered(StepKind.LLM):
            factory.register_singleton(StepKind.LLM, lambda _: LLMExecutor())
        self.executor_factory = factory
        self._memory_path = Path(spec.memory_file)

    def run(self) -> list[StepResponse]:
        """Execute each step in order and persist summary output."""

        responses: list[StepResponse] = []
        for step in self.spec.steps:
            request = StepRequest(
                step_id=step.id,
                name=step.name,
                kind=step.kind,
                correlation_id=f"step-{step.id}",
                input=step.input_template or "",
                memory_text=self._read_memory(),
                config=step.config,
            )
            self._notify_start(request)
            executor = self.executor_factory.create(step.kind)
            response = executor.execute(request)
            responses.append(response)
            if response.status == "fail":
                self._notify_error(request, response)
                self._append_memory(self._format_error(step.name, response))
                break
            self._notify_finish(request, response)
            self._append_memory(self._format_summary(step.name, response))
        return responses

    def _read_memory(self) -> str:
        if not self._memory_path.exists():
            return ""
        return self._memory_path.read_text(encoding="utf-8")

    def _append_memory(self, line: str) -> None:
        self._memory_path.parent.mkdir(parents=True, exist_ok=True)
        with self._memory_path.open("a", encoding="utf-8") as handle:
            handle.write(f"{line}\n")

    def _format_summary(self, step_name: str, response: StepResponse) -> str:
        result = response.result
        if isinstance(result, dict):
            message = result.get("message") or str(result)
        else:
            message = str(result)
        return f"- {step_name}: {message}"

    @staticmethod
    def _format_error(step_name: str, response: StepResponse) -> str:
        detail = response.error or "unknown error"
        return f"- {step_name}: failed ({detail})"

    def _notify_start(self, request: StepRequest) -> None:
        if self.observer:
            self.observer.on_step_start(request)

    def _notify_finish(self, request: StepRequest, response: StepResponse) -> None:
        if self.observer:
            self.observer.on_step_finish(request, response)

    def _notify_error(self, request: StepRequest, response: StepResponse) -> None:
        if self.observer:
            self.observer.on_step_error(request, response)


__all__ = ["WorkflowOrchestrator"]
