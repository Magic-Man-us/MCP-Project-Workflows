# Available Workflows

This document lists the available multistep workflows in this MCP project for use with Cline slash commands.

## Software Development Workflows

### Python Development Workflow

**Directory**: `workflows/python_development_workflow/`

**Description**: A comprehensive 4-step workflow for building production-ready Python applications following best practices (Pydantic, type hints, testing).

**Steps**:
1. Gather Python Requirements - Analyze dependencies, constraints, and specifications
2. Design Python Architecture - Plan data models, interfaces, and implementation
3. Implement Python Code - Write type-safe, documented production code
4. Test and Validate - Run comprehensive tests and static analysis

**Best Practices Enforced**:
- Pydantic v2 for data validation
- Type hints with mypy compatibility
- Black and isort formatting
- ruff linting and fixes
- pytest testing with coverage
- Security and dependency management

**Usage**: Suitable for web APIs, CLI tools, data processing, and general Python development.

**Command**: `python -m mcp_workflows.cli run python_development_workflow --goal "Your Python development task here"`

## Other Workflows

### Structured Demo
**Directory**: `workflows/structured_demo/`
**Description**: General software development workflow (requirements, design, implement, test)
**Command**: `python -m mcp_workflows.cli run structured_demo`

### Base Task Demo
**Directory**: `workflows/base_task_demo/`
**Description**: Uses base task templates for code development
**Command**: `python -m mcp_workflows.cli run base_task_demo`

### Test Workflows
Various test workflow configurations available in `workflows/run_test_workflow/`, `workflows/my_test_workflow/`, etc.

## Creating Custom Workflows

To create your own multistep workflow:

1. Create a directory under `workflows/`
2. Add `workflow.yaml` with steps, tasks, and LLM prompts
3. Add `memory.md` for session continuity
4. Optionally add `README.md` and config files

Run with: `python -m mcp_workflows.cli run <workflow_directory_name> --goal "Your goal"`
