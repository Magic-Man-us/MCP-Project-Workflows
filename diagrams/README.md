# MCP Workflow Builder System - Complete Guide

## What is MCP Workflow Builder?

MCP (Model Context Protocol) Workflow Builder is a **production-ready Python framework** for creating, managing, and executing complex workflows that combine machine learning, automation, and human-in-the-loop processes. It's designed specifically for scenarios where you need **deterministic, auditable workflows** that can integrate AI models (LLMs), automated scripts, and manual steps.

### Core Purpose
- **Note-taking and Memory**: Persistent memory files track progress across workflow executions
- **Structured Development**: Enforce systematic approaches to complex tasks (code development, documentation, research)
- **AI + Automation**: Combine LLM capabilities with shell scripts, Python automation, and manual oversight
- **Reusability**: Create templates for common workflows (design → implement → test patterns)

## Architecture Overview

### Key Components

#### 1. **WorkflowSpec** - The Immutable Heart
A frozen dataclass that defines a complete workflow:
```python
@dataclass(frozen=True)
class WorkflowSpec:
    goal: str                    # "Write production-ready code for task X"
    memory_file: str            # "memory.md" - persistent context
    tasks: tuple[TaskSpec, ...] # Reusable documents/instructions
    steps: tuple[StepSpec, ...] # Executable workflow units
```

#### 2. **WorkflowBuilder** - Fluent Construction API
Builds workflows incrementally using chain-able methods:
```python
WorkflowBuilder.start() \
    .with_goal("Build a web app") \
    .memory("memory.md") \
    .register_task("requirements", file="tasks/reqs.md") \
    .add_step("Design", kind="llm", uses=["requirements"]) \
    .compile()
```

#### 3. **WorkflowOrchestrator** - Execution Engine
Executes compiled workflows step-by-step:
```python
orchestrator = WorkflowOrchestrator(spec)
responses = orchestrator.run()  # Returns StepResponse list
```

#### 4. **Executors** - Pluggable Execution Strategies
Different ways to execute steps:
- **LLM**: Uses language models (currently returns canned responses)
- **Shell**: Executes shell commands
- **Python**: Runs Python scripts

### Real-World Usage Example

Based on your `my_test_workflow/workflow.yaml`:

```yaml
goal: Write production-ready code for the specified task
memory_file: memory.md
tasks:
- id: requirements
  text: "# Detailed requirements gathering instructions..."
steps:
- id: 1
  name: Gather Requirements
  kind: llm
  uses: [requirements]  # References the requirements task
```

This creates a **guidance-based workflow** where each step gets relevant documentation injected as context.

## How to Use MCP Workflow Builder

### Quick Start - Using Templates

```python
from mcp_workflows.templates import get_template, create_workflow_from_template

# Use a predefined template (code_workflow includes requirements/design/implement/test)
template = get_template("code_workflow")
workflow_path = create_workflow_from_template(template, Path("workflows/my_app"))
```

### Manual Builder Pattern

```python
from mcp_workflows.builder import WorkflowBuilder
from mcp_workflows.spec import StepKind
from pathlib import Path

builder = WorkflowBuilder.start()

# Basic configuration
builder.with_goal("Create a React component library")
builder.memory("workflows/component_lib/memory.md")

# Register reusable documentation
builder.register_task(
    "design_principles",
    text="# Design Principles\n- Use TypeScript\n- Follow atomic component patterns..."
)

builder.register_task(
    "component_specs",
    file="workflows/component_lib/specs/component_specs.md"
)

# Define steps
builder.add_step(
    name="Design Architecture",
    kind=StepKind.LLM,
    doc="Design the component library structure",
    uses=["design_principles"],
    input_template="Design components for: {feature_name}",
    config={"temperature": 0.3}
)

builder.add_step(
    name="Create Components",
    kind=StepKind.LLM,
    doc="Implement the designed components",
    uses=["component_specs", "design_principles"],
    config={"model": "gpt-4"}
)

# Compile and save
spec = builder.compile()
builder.emit_yaml("workflows/component_lib/workflow.yaml")
```

### Executing Workflows

```python
from mcp_workflows.orchestrator import WorkflowOrchestrator

# Load compiled spec
orchestrator = WorkflowOrchestrator(spec)

# Optional: Add observers for monitoring
class WorkflowMonitor:
    def on_step_start(self, request):
        print(f"Starting: {request.name}")

    def on_step_finish(self, request, response):
        print(f"Completed: {request.name} -> {response.status}")

orchestrator_with_monitoring = WorkflowOrchestrator(
    spec,
    observer=WorkflowMonitor()
)

# Execute
responses = orchestrator.run()
print(f"Workflow completed with {len(responses)} steps")
```

## Deep Dive: Understanding Each Component

### Task System: Reusability & Context

**Tasks vs Steps:**
- **Task**: Reusable documentation/definition (like a function that can be called multiple times)
- **Step**: Single execution instance that references tasks

**Task Types:**
1. **File-based**: `register_task("api_docs", file="docs/api.md")`
2. **Text-based**: `register_task("instructions", text="Step-by-step guide...")`

**Advanced Task Usage:**
```python
# Multi-context steps
builder.add_step(
    name="Code Review",
    kind="llm",
    uses=["requirements", "design", "implementation"],  # 3 different contexts
    input_template="Review this code against requirements and design"
)
```

### Step Configuration Deep Dive

**StepSpec Fields:**
- `id`: Sequential integer identifier
- `name`: Descriptive name
- `kind`: Execution strategy (llm/shell/python)
- `doc`: Documentation (why this step exists)
- `uses`: List of task IDs (context documents)
- `input_template`: Dynamic input format
- `config`: Executor-specific parameters
- `branches`: Conditional jumps
- `next_step`: Custom order override

**Input Templates:**
```python
# Templates with variable substitution
input_template="Analyze {feature_name} for {target_platform}"

# Under the hood, gets formatted with step config
formatted = "Analyze authentication for mobile platform"
```

**Branching Logic:**
```python
builder.add_step(
    name="Code Review",
    # ... other fields
    branches=[
        Branch(when="failed linting", goto=5),  # Jump to fix step
        Branch(when="tests failed", goto=7)     # Jump to test fixing
    ]
)
```

### Memory System: Persistent Context

**What gets stored:**
- Step execution summaries
- Error messages (if any)
- Key artifacts/output excerpts

**Memory Format:**
```
- Gather Requirements: Complete requirements gathered for user auth
- Design Solution: Designed JWT-based authentication with refresh tokens
- Implement Code: Created Login component, UserContext, ProtectedRoute
- Test and Review: Tests passing, code quality good
```

**Memory Persistence Benefits:**
- **Resume workflows**: Restart after interruptions
- **Context awareness**: Future steps see what was done
- **Auditable history**: Complete execution trails
- **Debugging**: Easy to spot where failures occurred

## Customization & Extension

### Creating Custom Templates

```python
from mcp_workflows.templates import WorkflowTemplate
from mcp_workflows.spec import StepKind

class DataScienceTemplate(WorkflowTemplate):
    name = "data_science"

    def __init__(self):
        super().__init__()
        self.goal = "Build and deploy ML model for prediction task"
        self.steps = [
            StepSpec(
                id=1, name="Data Exploration",
                kind=StepKind.PYTHON,
                doc="Analyze dataset characteristics"
            ),
            StepSpec(
                id=2, name="Feature Engineering",
                kind=StepKind.LLM,
                doc="Design features for model input"
            ),
            StepSpec(
                id=3, name="Model Building",
                kind=StepKind.PYTHON,
                doc="Train and evaluate models"
            )
        ]
```

### Custom Executors

```python
from mcp_workflows.executors import Executor
from mcp_workflows.spec import StepRequest, StepResponse

class RESTAPIExecutor(Executor):
    def execute(self, request: StepRequest) -> StepResponse:
        # Execute HTTP API calls
        response = requests.post(f"http://api.example.com/{request.name}")
        return StepResponse(
            status="ok" if response.ok else "fail",
            result=response.json(),
            error=response.text if not response.ok else None
        )

# Register custom executor
factory = ExecutorFactory.default()
factory.register_instance(StepKind.LLM, CustomLLMExecutor())
```

### Advanced Dependency Injection

```python
from mcp_workflows.factories import ServiceContainer, ExecutorFactory

# Custom container with external services
container = ServiceContainer()

# Register singletons
container.register_singleton("api_client", lambda _: requests.Session())
container.register_singleton(
    "llm_service",
    lambda c: OpenAIClient(api_key=os.env["OPENAI_API_KEY"])
)

# Create factory and register custom executors
factory = ExecutorFactory(container)
factory.register_factory(
    "ml_prediction",
    lambda c: MLExecutor(c.resolve("api_client"))
)
```

## Tips, Tricks & Best Practices

### 1. Memory Management
```python
# Custom memory formatter for better context
def summarize_step(name: str, response: StepResponse) -> str:
    if response.status == "ok":
        # Extract key insights
        return f"- {name}: ✓ {response.result.get('key_outcome', 'completed')}"
    else:
        return f"- {name}: ✗ Failed - {response.error}"
```

### 2. Template Inheritance
```python
class SpecializedCodeTemplate(CodeWorkflowTemplate):
    """Extend base template with specific steps"""

    def __init__(self, tech_stack: str):
        super().__init__()
        self.steps.append(
            StepSpec(
                id=5,
                name=f"Tech Stack Setup ({tech_stack})",
                kind=StepKind.SHELL,
                doc=f"Initialize {tech_stack} project structure"
            )
        )
```

### 3. Conditional Workflows
```python
def build_deployment_workflow(env: str):
    builder = WorkflowBuilder.start().with_goal("Deploy application")

    steps = [
        ("build", StepKind.SHELL, "Build application"),
        ("test", StepKind.PYTHON, "Run test suite"),
    ]

    if env == "production":
        steps.extend([
            ("staging_deploy", StepKind.SHELL, "Deploy to staging"),
            ("integration_test", StepKind.PYTHON, "Verify staging"),
        ])

    steps.append(("production_deploy", StepKind.SHELL, "Deploy to production"))

    for name, kind, doc in steps:
        builder.add_step(name=name, kind=kind, doc=doc)

    return builder.compile()
```

### 4. Observer Patterns for Monitoring
```python
class ComprehensiveMonitor:
    def on_step_start(self, request: StepRequest):
        logger.info(f"[{request.correlation_id}] Starting {request.name}")

    def on_step_finish(self, request: StepRequest, response: StepResponse):
        if response.result and 'artifacts' in response.result:
            # Save artifacts to persistent storage
            save_artifacts(request.name, response.result['artifacts'])

    def on_step_error(self, request: StepRequest, response: StepResponse):
        # Send notifications
        send_notification(f"Step failed: {request.name} - {response.error}")
        # Auto-retry logic
        if should_retry(response.error):
            return RetryDecision(retries_left=3)
```

### 5. Parallel Subworkflows
```python
def create_parallel_validation_workflow():
    """Run validation steps in parallel (simulate)"""

    parallel_steps = [
        ("security_audit", StepKind.PYTHON),
        ("performance_test", StepKind.SHELL),
        ("accessibility_check", StepKind.LLM),
    ]

    # Execute each parallel step
    # Note: Current system is sequential, but this pattern shows extensibility
    for step_name, step_kind in parallel_steps:
        builder.add_step(name=f"Parallel {step_name}", kind=step_kind)
```

### 6. Configuration-Driven Workflows
```python
@dataclass
class WorkflowConfig:
    name: str
    steps: list[dict]
    memory_strategy: str = "accumulate"

def build_from_config(config: WorkflowConfig):
    builder = WorkflowBuilder.start().with_goal(f"Execute {config.name}")

    for step_config in config.steps:
        builder.add_step(**step_config)

    return builder.compile()
```

## Common Patterns & Use Cases

### 1. Research Assistant Workflow
```
1. Literature Review (LLM + Web)
2. Hypothesis Formation (LLM)
3. Experiment Planning (LLM)
4. Data Collection (Python)
5. Analysis (Python)
6. Results Interpretation (LLM)
```

### 2. Code Development Pipeline
```
1. Requirements Analysis (LLM)
2. Architecture Design (LLM)
3. Implementation (LLM/Programming)
4. Unit Testing (Python)
5. Integration Testing (Shell)
6. Documentation (LLM)
```

### 3. Content Creation Pipeline
```
1. Topic Research (LLM)
2. Content Planning (LLM)
3. Draft Creation (LLM)
4. Fact Checking (LLM)
5. Editing & Polish (LLM)
6. SEO Optimization (LLM)
```

### 4. Business Process Automation
```
1. Data Import (Shell)
2. Data Validation (Python)
3. Report Generation (LLM + Data)
4. Approval Routing (Custom Logic)
5. Distribution (Shell/Email)
```

## Troubleshooting Guide

### Common Issues

**1. Executor Not Found**
```python
# Problem: StepKind.LLM executor not registered
# Solution: Use ExecutorFactory.default() or register explicitly
```

**2. Memory File Race Conditions**
```python
# Problem: Concurrent workflow access
# Solution: Use file locking or queue-based execution
import fcntl
with open(memory_file, 'a') as f:
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
```

**3. Long-Running Steps Timeout**
```python
# Problem: Steps taking too long
# Solution: Add timeout configuration
builder.add_step(
    name="Long Process",
    kind="shell",
    config={"timeout": 300}  # 5 minutes
)
```

**4. Memory File Size Explosion**
```python
# Problem: Memory file growing too large
# Solution: Implement memory rotation or summarization
```

### Debug Mode
```python
class DebugMonitor:
    def on_step_start(self, request):
        print(f"DEBUG: Request: {request}")
        print(f"DEBUG: Input: {request.input}")
        print(f"DEBUG: Config: {request.config}")

    def on_step_finish(self, request, response):
        print(f"DEBUG: Response: {response}")
        print(f"DEBUG: Memory updated: {response.status}")
```

## Performance Optimization

### 1. Executor Pooling
```python
# Reuse expensive resources
factory.register_singleton(
    StepKind.LLM,
    lambda: CachedLLMExecutor(model_cache_size=10)
)
```

### 2. Step Batch Processing
```python
# Group similar steps
# Implementation needed: BatchExecutor that processes multiple steps at once
```

### 3. Memory Optimization
```python
# Clear old memory for long workflows
def compress_memory(memory_text: str, max_lines: int = 1000) -> str:
    lines = memory_text.split('\n')
    if len(lines) > max_lines:
        # Keep recent lines + summary of older ones
        return summarize_old_lines(lines[:-max_lines]) + '\n'.join(lines[-max_lines:])
    return memory_text
```

## Security Considerations

### 1. File System Access
```python
# Sandbox file operations
import os
import pathlib

def safe_file_path(user_path: str, allowed_dir: str) -> pathlib.Path:
    resolved = pathlib.Path(allowed_dir) / user_path
    resolved = resolved.resolve()
    if not str(resolved).startswith(allowed_dir):
        raise ValueError("Path traversal attempt")
    return resolved
```

### 2. Command Injection Prevention
```python
# Use argument lists, not string concatenation
subprocess.run(["bash", "-c", "safe command"], shell=False)
```

### 3. API Key Management
```python
# Environment-based secrets
import os
api_key = os.environ.get("SECURE_API_KEY")
if not api_key:
    raise ValueError("API key required")
```

## Advanced Features & Extensions

### 1. Custom Step Kinds
```python
from mcp_workflows.spec import StepKind

try:
    # Register new kind
    StepKind.DATABASE = "database"
    StepKind.NOTIFICATION = "notification"
except:
    # If enum modification fails, create new types
    pass
```

### 2. Workflow Composition
```python
class WorkflowComposer:
    def __init__(self):
        self.workflows = {}

    def register(self, name: str, spec: WorkflowSpec):
        self.workflows[name] = spec

    def compose(self, names: list[str]) -> WorkflowSpec:
        """Merge multiple workflows into one"""
        # Implementation for workflow composition
```

### 3. Dynamic Step Generation
```python
def generate_steps_from_config(config_data: dict) -> list[StepSpec]:
    """Generate steps from configuration data"""
    steps = []
    for i, step_config in enumerate(config_data['steps'], 1):
        steps.append(StepSpec(
            id=i,
            name=step_config['name'],
            kind=StepKind(step_config['type']),
            config=step_config.get('config', {})
        ))
    return steps
```

### 4. Real-Time Monitoring GUI
```python
# Integration with web frameworks for dashboards
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/workflow/status')
def get_status():
    return jsonify(active_workflows)
```

## Real-World Examples

### Example 1: Automated Code Review
```python
builder = WorkflowBuilder.start() \
    .with_goal("Comprehensive code review") \
    .register_task("code_quality", file="standards.md") \
    .register_task("security_guidelines", file="security.md")

builder.add_step("Style Check", StepKind.SHELL, uses=["code_quality"])
builder.add_step("Security Scan", StepKind.PYTHON, uses=["security_guidelines"])
builder.add_step("Logic Review", StepKind.LLM, uses=["code_quality", "security_guidelines"])

spec = builder.compile()
```

### Example 2: Data Pipeline
```python
def create_etl_workflow(source: str, target: str):
    return WorkflowBuilder.start() \
        .with_goal(f"ETL from {source} to {target}") \
        .add_step("Extract", StepKind.PYTHON, config={"source": source}) \
        .add_step("Transform", StepKind.PYTHON, config={"transform_rules": "..."}) \
        .add_step("Load", StepKind.PYTHON, config={"target": target}) \
        .add_step("Validate", StepKind.PYTHON) \
        .compile()
```

### Example 3: Multi-Modal AI Workflow
```python
builder.add_step(
    "Image Analysis",
    kind="llm",
    config={"model": "gpt-4-vision"},
    uses=["analysis_guidelines"]
)

builder.add_step(
    "Text Summarization",
    kind="llm",
    config={"model": "claude-2"},
    uses=["summarization_template"]
)
```

## Future Extensions & Roadmap

### Planned Features
- **Parallel Execution**: Run steps concurrently when dependencies allow
- **Conditional Step Evaluation**: Skip steps based on previous results
- **Sub-workflow Calling**: Invoke other workflows as steps
- **Event Streaming**: Real-time progress notifications
- **Configuration Hot Reload**: Modify workflows without restart
- **Version Control Integration**: Track workflow changes over time

### Plugin Architecture
```python
# Planned plugin system
from mcp_workflows import plugin

@plugin.register_executor("slack")
class SlackExecutor(Executor):
    def execute(self, request):
        # Send Slack notifications
        pass
```

## Conclusion

MCP Workflow Builder provides a **structured, extensible framework** for creating complex workflows that combine AI, automation, and human oversight. Key strengths:

- **Immutable Specifications**: Thread-safe, testable workflow definitions
- **Persistent Memory**: Context preservation across executions
- **Pluggable Executors**: Easy to add new execution types
- **Template System**: Reusable workflow patterns
- **Observer Pattern**: Rich monitoring and intervention points

Whether you're building AI-assisted development tools, automated research pipelines, or business process automation, MCP Workflow Builder provides the foundation for **reliable, auditable, and extensible workflow systems**.
