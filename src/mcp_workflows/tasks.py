"""Built-in task definitions for workflow templates."""

from __future__ import annotations

# Task prompts for code writing workflows
REQUIREMENTS_MD = """# Requirements Analysis

- Gather all functional requirements
- Identify constraints and edge cases
- Clarify input/output specifications
- Note dependencies and prerequisites"""

DESIGN_MD = """# Design Phase

- Architect the solution structure
- Plan algorithms and data flow
- Define interfaces and modules
- Consider error handling"""

IMPLEMENTATION_MD = """# Code Implementation

- Write clean, readable code
- Follow language best practices
- Add meaningful comments
- Handle exceptions properly"""

TESTING_MD = """# Testing and Review

- Write unit tests for key functions
- Test edge cases and error conditions
- Review code for bugs and optimization
- Suggest improvements"""


__all__ = [
    "DESIGN_MD",
    "IMPLEMENTATION_MD",
    "REQUIREMENTS_MD",
    "TESTING_MD",
]
