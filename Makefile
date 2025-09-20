# Makefile for MCP-Project-Workflows

# Virtual environment paths
VENV = .venv_workflows/bin
PYTHON = $(VENV)/python
PIP = $(VENV)/pip

.PHONY: help install test lint format docs clean run coverage

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install dependencies
	$(PIP) install -e .[dev]

test: ## Run tests
	$(PYTHON) -m pytest

lint: ## Lint code with Ruff
	$(PYTHON) -m ruff check .

format: ## Format code with Ruff and Black
	$(PYTHON) -m ruff format .
	$(PYTHON) -m black .

docs: ## Build documentation with Sphinx
	$(PYTHON) -m sphinx.cmd.build docs docs/_build

clean: ## Clean build artifacts
	rm -rf docs/_build
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm -rf *.pyc

run: ## Run the main script
	$(PYTHON) -m mcp_workflows.main

coverage: ## Run tests with coverage
	$(PYTHON) -m pytest