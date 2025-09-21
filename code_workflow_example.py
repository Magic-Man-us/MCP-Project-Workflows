#!/usr/bin/env python3
"""
Example: Creating a multi-step workflow for writing code.
"""

from pathlib import Path

from mcp_workflows.builder import WorkflowBuilder

# Define task prompts (you can put these in separate .md files)
requirements_md = """# Requirements Analysis

- Gather all functional requirements
- Identify constraints and edge cases
- Clarify input/output specifications
- Note dependencies and prerequisites"""

design_md = """# Design Phase

- Architect the solution structure
- Plan algorithms and data flow
- Define interfaces and modules
- Consider error handling"""

implementation_md = """# Code Implementation

- Write clean, readable code
- Follow language best practices
- Add meaningful comments
- Handle exceptions properly"""

testing_md = """# Testing and Review

- Write unit tests for key functions
- Test edge cases and error conditions
- Review code for bugs and optimization
- Suggest improvements"""

def create_code_writing_workflow():
    """Create a multi-step workflow for writing code."""

    builder = (
        WorkflowBuilder.start()
        .with_goal("Write production-ready code for the specified task")
        .memory("code_memory.md")
    )

    # Register tasks
    builder.register_task("requirements", text=requirements_md)
    builder.register_task("design", text=design_md)
    builder.register_task("implement", text=implementation_md)
    builder.register_task("test", text=testing_md)

    # Add steps in sequence
    builder.add_step(
        "Gather Requirements",
        doc="Collect and analyze all requirements for the coding task",
        uses=["requirements"],
    )

    builder.add_step(
        "Design Solution",
        doc="Plan the architecture and approach for implementation",
        uses=["requirements", "design"],
    )

    builder.add_step(
        "Implement Code",
        doc="Write the actual code following the design plan",
        uses=["design", "implement"],
    )

    builder.add_step(
        "Test and Review",
        doc="Test the code, review for quality, and suggest improvements",
        uses=["implement", "test"],
    )

    return builder

if __name__ == "__main__":
    # Create and emit the workflow
    builder = create_code_writing_workflow()
    output_path = Path("workflows/code_workflow.yaml")
    builder.emit_yaml(output_path)

    print(f"Multi-step code writing workflow created: {output_path}")
    print("\nYou can run it with:")
    print(f"python -m mcp_workflows.main --goal 'Write a Python function to sort a list' --out {output_path} --memory code_memory.md --run")
