"""Factories and dependency injection helpers for workflow executors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, cast

from .executors import Executor, LLMExecutor
from .spec import StepKind


@dataclass(slots=True)
class _Provider:
    """Internal descriptor storing provider metadata."""

    factory: Callable[["ServiceContainer"], Any]
    singleton: bool


class ServiceContainer:
    """Minimalistic dependency injection container."""

    def __init__(self) -> None:
        self._providers: dict[str, _Provider] = {}
        self._singletons: dict[str, Any] = {}

    def register_factory(
        self,
        key: str,
        factory: Callable[["ServiceContainer"], Any],
        *,
        override: bool = False,
    ) -> None:
        """Register ``factory`` to create new instances for ``key`` each request."""

        self._set_provider(key, _Provider(factory=factory, singleton=False), override)

    def register_singleton(
        self,
        key: str,
        factory: Callable[["ServiceContainer"], Any],
        *,
        override: bool = False,
    ) -> None:
        """Register ``factory`` producing a singleton instance for ``key``."""

        self._set_provider(key, _Provider(factory=factory, singleton=True), override)

    def register_instance(self, key: str, instance: Any, *, override: bool = False) -> None:
        """Register a pre-built ``instance`` as a singleton for ``key``."""

        if not override and self.is_registered(key):
            msg = f"Service '{key}' is already registered"
            raise ValueError(msg)
        self._providers.pop(key, None)
        self._singletons[key] = instance

    def resolve(self, key: str) -> Any:
        """Return the dependency associated with ``key``."""

        if key in self._singletons:
            return self._singletons[key]
        provider = self._providers.get(key)
        if provider is None:
            msg = f"Service '{key}' has not been registered"
            raise LookupError(msg)
        instance = provider.factory(self)
        if provider.singleton:
            self._singletons[key] = instance
        return instance

    def is_registered(self, key: str) -> bool:
        """Return ``True`` if ``key`` exists in the container."""

        return key in self._providers or key in self._singletons

    def clear_singletons(self) -> None:
        """Discard cached singleton instances (useful for deterministic tests)."""

        self._singletons.clear()

    def _set_provider(self, key: str, provider: _Provider, override: bool) -> None:
        if not override and self.is_registered(key):
            msg = f"Service '{key}' is already registered"
            raise ValueError(msg)
        self._singletons.pop(key, None)
        self._providers[key] = provider


class ExecutorFactory:
    """Factory responsible for supplying executors for workflow steps."""

    _NAMESPACE = "executor"

    def __init__(self, container: ServiceContainer | None = None) -> None:
        self._container = container or ServiceContainer()

    @property
    def container(self) -> ServiceContainer:
        """Expose the underlying container for advanced configuration."""

        return self._container

    def register_factory(
        self,
        kind: StepKind,
        builder: Callable[[ServiceContainer], Executor],
        *,
        override: bool = False,
    ) -> None:
        """Register ``builder`` to create a fresh executor for ``kind`` each time."""

        self._container.register_factory(self._key(kind), builder, override=override)

    def register_singleton(
        self,
        kind: StepKind,
        builder: Callable[[ServiceContainer], Executor],
        *,
        override: bool = False,
    ) -> None:
        """Register ``builder`` whose result is cached and reused for ``kind``."""

        self._container.register_singleton(self._key(kind), builder, override=override)

    def register_instance(
        self,
        kind: StepKind,
        executor: Executor,
        *,
        override: bool = False,
    ) -> None:
        """Register a pre-constructed executor for ``kind``."""

        self._container.register_instance(self._key(kind), executor, override=override)

    def create(self, kind: StepKind) -> Executor:
        """Create or retrieve the executor matching ``kind``."""

        try:
            executor = self._container.resolve(self._key(kind))
        except LookupError as exc:
            msg = f"No executor registered for step kind '{kind.value}'"
            raise ValueError(msg) from exc
        return cast(Executor, executor)

    def is_registered(self, kind: StepKind) -> bool:
        """Return ``True`` if an executor has been registered for ``kind``."""

        return self._container.is_registered(self._key(kind))

    @classmethod
    def default(cls) -> "ExecutorFactory":
        """Create a factory seeded with the default LLM executor."""

        factory = cls()
        factory.register_singleton(StepKind.LLM, lambda _: LLMExecutor())
        return factory

    def _key(self, kind: StepKind) -> str:
        return f"{self._NAMESPACE}:{kind.value}"


__all__ = ["ExecutorFactory", "ServiceContainer"]
