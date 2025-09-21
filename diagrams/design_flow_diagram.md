# Design Flow Diagram

```mermaid
flowchart TD
    %% Start and Initialization
    START([Start Workflow Design]) --> A[Define Goal & Memory File]

    %% Template Usage
    A --> B{Use Template?}
    B -->|Yes| C[Select WorkflowTemplate]
    B -->|No| D[Create WorkflowBuilder]

    C --> E[Get Template Structure]
    E --> F[Convert BaseTasks to TaskSpecs]
    F --> D

    %% Builder Pattern Flow
    D --> G[with_goal('goal')]
    G --> H[memory('path')]

    H --> I[Register Tasks]
    I --> J{Register more tasks?}
    J -->|Yes| K[register_task(id, file/text)]
    K --> J
    J -->|No| L[Add Steps]

    L --> M{Add more steps?}
    M -->|Yes| N[add_step(name, kind, uses, config)]
    N --> M
    M -->|No| O[end() - finalize]

    %% Compilation and Execution
    O --> P[compile() -> WorkflowSpec]
    P --> Q{Ready to Execute?}
    Q -->|No| R[emit_yaml(path) - Save]
    Q -->|Yes| S[Create WorkflowOrchestrator]

    R --> T[Workflow YAML File]
    T --> Q

    S --> U[Resolve Executors from Factory]
    U --> V[Load Memory File]
    V --> W[Initialize Observers]

    %% Execution Loop
    W --> X[For each Step in WorkflowSpec]
    X --> Y[Create StepRequest]
    Y --> Z[Execute Step via Executor]
    Z --> AA[Generate StepResponse]

    AA --> BB{Status Check}
    BB -->|OK| CC[Notify Finish]
    BB -->|Fail| DD[Notify Error]
    BB -->|Retry| EE[Handle Retry Logic]

    CC --> FF[Append to Memory]
    DD --> GG[Terminate Execution]
    FF --> HH{Has Next Step?}
    HH -->|Yes| X
    HH -->|No| II[Complete Workflow]
    EE --> X

    GG --> II

    II --> JJ[Return StepResponses]

    %% Styling
    classDef templateClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef builderClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef execClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef decisionClass fill:#fff3e0,stroke:#e65100,stroke-width:2px

    class C,E,F templateClass
    class D,G,H,I,J,K,L,M,N,O,P builderClass
    class S,U,V,W,X,Y,Z,AA,BB,FF,HH execClass
    class B,J,M,Q,BB,HH decisionClass

    START([Start]):::execClass
    JJ([End]):::execClass
```

## Workflow Design Flow Explanation

### 1. **Initialization Phase**
- Define the overall goal and memory file path
- Choose between using a predefined template or building from scratch

### 2. **Template Application (Optional)**
- Select a WorkflowTemplate (e.g., "code_workflow")
- Extract base tasks and convert to TaskSpecs
- Use template structure as starting point

### 3. **Incremental Building**
- Use fluent WorkflowBuilder API to add:
  - Goal and memory configuration
  - Reusable tasks (documents/files)
  - Sequential execution steps

### 4. **Compilation**
- Produce immutable WorkflowSpec
- Optionally serialize to YAML for persistence

### 5. **Execution Preparation**
- Create WorkflowOrchestrator with spec
- Register appropriate executors for each step kind
- Initialize observers for lifecycle events
- Load existing memory context

### 6. **Step-by-Step Execution**
For each step:
- Build StepRequest with context and configuration
- Route to appropriate Executor based on step kind
- Handle response status (success/fail/retry)
- Update persistent memory
- Notify observers of progress

### 7. **Completion**
- Return collected StepResponses
- Memory persists for future runs or inspection

## Key Benefits

- **Separation of Concerns**: Build phase vs execution phase
- **Immutability**: Specs cannot change after compilation
- **Reusability**: Tasks and templates reduce duplication
- **Observability**: Hooks for monitoring and debugging
- **Persistence**: Memory maintains context across executions
