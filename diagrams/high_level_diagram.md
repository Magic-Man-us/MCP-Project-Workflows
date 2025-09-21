# High-Level Architecture Diagram

```mermaid
graph TD
    A[User Input] --> B[WorkflowBuilder]
    B --> C[WorkflowSpec]
    C --> D[WorkflowOrchestrator]
    D --> E[Executors]

    B --> F[BaseTask]
    F --> G[TaskSpec]

    B --> H[StepSpec]

    D --> I[StepRequest]
    E --> J[StepResponse]
    J --> D

    D --> K[Memory File]

    style A fill:#f9f,stroke:#333,stroke-width:4px
    style K fill:#ff9,stroke:#333,stroke-width:2px
```

## Component Overview

- **WorkflowBuilder**: Fluent API for building workflow specifications
- **WorkflowSpec**: Immutable specification containing goal, tasks, and steps
- **WorkflowOrchestrator**: Executes steps in order using registered executors
- **Executors**: Implement step execution (LLM, Shell, Python)
- **BaseTask/TaskSpec**: Reusable task definitions and documents
- **StepSpec**: Individual executable units with configuration
- **Memory File**: Persistent memory across workflow executions

## Key Relationships

- Builder produces immutable Specs
- Orchestrator consumes Specs and produces execution Requests/Responses
- Steps reference Tasks for documentation and context
- Memory persists between executions for continuity
