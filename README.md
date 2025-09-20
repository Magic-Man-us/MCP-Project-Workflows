# MCP Workflows

A basic Python project for MCP workflows.

## Setup

1. Ensure you have Python 3.12+ installed
2. Create and activate virtual environment (already done)
3. Install dependencies: `make install`

## Usage

Run the main script: `make run` or `python -m mcp_workflows.main`

## Project Structure

```
├── src/
│   └── mcp_workflows/
│       ├── __init__.py
│       └── main.py
├── tests/
│   └── test_main.py
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