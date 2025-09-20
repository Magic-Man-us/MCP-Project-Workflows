# MCP Workflows

A basic Python project for MCP workflows.

## Setup

1. Ensure you have Python 3.12+ installed
2. Create and activate virtual environment (already done)
3. Install dependencies: `make install`

## Usage

Generate a demo workflow YAML file:

```bash
python -m mcp_workflows.main --goal "Sketch a sample workflow" --out workflows/demo.yaml --memory memory.md
```

The command uses the fluent builder to create a workflow specification and saves it to the
requested path. Add `--run` to execute the canned orchestrator and append a summary line to the
memory file.

## Project Structure

```
├── src/
│   └── mcp_workflows/
│       ├── __init__.py
│       ├── builder.py
│       ├── cli.py
│       ├── executors.py
│       ├── hooks.py
│       ├── main.py
│       ├── orchestrator.py
│       └── spec.py
├── tasks/
│   ├── normalize.md
│   └── quality_gate.md
├── tests/
│   ├── test_builder.py
│   ├── test_cli.py
│   └── test_orchestrator.py
├── workflows/
│   └── .gitkeep
├── docs/
├── pyproject.toml
├── Makefile
└── README.md
```

## Development Commands

Use the Makefile for common tasks:

- `make help` - Show all available commands
- `make install` - Install/update dependencies
- `make test` - Run tests with coverage
- `make run` - Run the main script
- `make lint` - Lint code with Ruff
- `make format` - Format code with Ruff and Black
- `make docs` - Build documentation
- `make clean` - Clean build artifacts