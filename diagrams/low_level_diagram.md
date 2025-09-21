# Low-Level Class Diagram

```mermaid
classDiagram
    class WorkflowBuilder {
        +start(): WorkflowBuilder
        +with_goal(goal: str): WorkflowBuilder
        +memory(path): WorkflowBuilder
        +register_task(task_id, file?, text?): WorkflowBuilder
        +add_step(name, kind?, uses?, config?): WorkflowBuilder
        +compile(): WorkflowSpec
        +emit_yaml(path): Path
        -_goal: str
        -_memory_file: str
        -_tasks: dict[str, TaskSpec]
        -_steps: list[StepSpec]
    }

    class WorkflowSpec {
        <<frozen>>
        +goal: str
        +memory_file: str
        +tasks: tuple[TaskSpec, ...]
        +steps: tuple[StepSpec, ...]
        +as_dict(): dict
    }

    class WorkflowOrchestrator {
        +WorkflowOrchestrator(spec, observer?, executors?, factory?)
        +run(): list[StepResponse]
        -_read_memory(): str
        -_append_memory(line: str): None
        -_format_summary(step_name, response): str
        -_notify_start(request): None
        -_notify_finish(request, response): None
        -_notify_error(request, response): None
    }

    class BaseTask {
        <<frozen>>
        +name: str
        +objective: str
        +description: str
        +sites_to_visit: tuple[str, ...]
        +substeps: tuple[str, ...]
        +prerequisites: tuple[str, ...]
        +instructions: str
        +expected_output: str
        +success_criteria: tuple[str, ...]
        +to_task_spec(): TaskSpec
    }

    class TaskSpec {
        <<frozen>>
        +id: str
        +file: str?
        +text: str?
        +as_dict(): dict
    }

    class StepSpec {
        <<frozen>>
        +id: int
        +name: str
        +kind: StepKind
        +doc: str
        +uses: tuple[str, ...]
        +input_template: str?
        +config: dict[str, Any]
        +branches: tuple[Branch, ...]
        +next_step: int?
        +as_dict(): dict
    }

    class Branch {
        <<frozen>>
        +when: str
        +goto: int
        +as_dict(): dict
    }

    class StepRequest {
        <<frozen>>
        +step_id: int
        +name: str
        +kind: StepKind
        +correlation_id: str
        +input: Any
        +memory_text: str
        +config: dict[str, Any]
    }

    class StepResponse {
        +status: Literal["ok", "retry", "fail"]
        +result: Any?
        +quality: str?
        +artifacts: tuple[str, ...]?
        +next_step: int?
        +error: str?
    }

    class Executor {
        <<interface>>
        +execute(request: StepRequest): StepResponse
    }

    class LLMExecutor {
        +execute(request: StepRequest): StepResponse
    }

    class ExecutorFactory {
        +register_factory(kind, builder): None
        +register_singleton(kind, builder): None
        +register_instance(kind, executor): None
        +create(kind): Executor
        +is_registered(kind): bool
        -_container: ServiceContainer
    }

    class ServiceContainer {
        +register_factory(key, factory): None
        +register_singleton(key, factory): None
        +register_instance(key, instance): None
        +resolve(key): Any
        +is_registered(key): bool
    }

    class WorkflowTemplate {
        +name: str
        +structure: Dict[str, str | None]
        +goal: str
        +memory_file: str
        +steps: list[StepSpec]
        +base_tasks: list[BaseTask]
        +tasks: list[TaskSpec]
    }

    class StepObserver {
        <<interface>>
        +on_step_start(request): None
        +on_step_finish(request, response): None
        +on_step_error(request, response): None
    }

    WorkflowBuilder ..> WorkflowSpec : compiles
    WorkflowBuilder ..> TaskSpec : creates
    WorkflowBuilder ..> StepSpec : creates

    WorkflowSpec --> TaskSpec : contains
    WorkflowSpec --> StepSpec : contains

    WorkflowOrchestrator --> WorkflowSpec : consumes
    WorkflowOrchestrator --> StepRequest : creates
    WorkflowOrchestrator --> StepResponse : receives
    WorkflowOrchestrator ..> Executor : uses factory
    WorkflowOrchestrator ..> StepObserver : notifies

    BaseTask --> TaskSpec : converts to

    StepSpec --> TaskSpec : references
    StepSpec --> Branch : contains
    StepSpec --> StepKind : uses

    StepRequest --> StepSpec : derived from
    StepResponse --> StepRequest : result of

    Executor <|-- LLMExecutor : implements

    ExecutorFactory --> ServiceContainer : uses
    ExecutorFactory --> Executor : creates

    WorkflowTemplate --> StepSpec : defines
    WorkflowTemplate --> BaseTask : defines
    WorkflowTemplate --> TaskSpec : derives

    StepObserver --> StepRequest : observes
    StepObserver --> StepResponse : observes
```

## Key Data Flows

1. **Build Phase**: WorkflowBuilder → TaskSpec/StepSpec → WorkflowSpec
2. **Execution Phase**: WorkflowSpec → WorkflowOrchestrator → StepRequest → Executor → StepResponse
3. **Memory**: Orchestrator reads/writes persistent memory file
4. **Templates**: WorkflowTemplate provides defaults for WorkflowBuilder

## Design Patterns

- **Builder Pattern**: Incremental building of complex objects
- **Factory Pattern**: Creation of executors via dependency injection
- **Observer Pattern**: Notification system for step lifecycle events
- **Template Method**: WorkflowTemplate providing reusable structures
