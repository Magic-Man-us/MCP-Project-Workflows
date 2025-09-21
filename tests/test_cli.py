"""CLI behaviour tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from mcp_workflows.cli import build_code_workflow
from mcp_workflows.cli import main as cli_main
from mcp_workflows.main import main as entry_main


def test_build_code_workflow_creates_yaml(tmp_path: Path) -> None:
    """The code workflow builder creates a complete workflow folder."""

    # Change to tmp_path for the test
    import os
    old_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        workflow_folder = build_code_workflow("test_workflow")
        assert workflow_folder.exists()
        assert (workflow_folder / "workflow.yaml").exists()
        assert (workflow_folder / "memory.md").exists()

        text = (workflow_folder / "workflow.yaml").read_text(encoding="utf-8")
        assert "goal" in text
        assert "tasks" in text
        assert "memory_file: memory.md" in text  # Relative path
    finally:
        os.chdir(old_cwd)


def test_cli_main_creates_workflow_folder(capsys: pytest.CaptureFixture[str]) -> None:
    """Invoking the CLI creates a workflow folder structure."""

    exit_code = cli_main(["my_test_workflow"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Code writing workflow 'my_test_workflow' created in:" in captured.out
    assert "workflows/my_test_workflow" in captured.out


def test_cli_main_run_executes_workflow(capsys: pytest.CaptureFixture[str]) -> None:
    """Running the CLI with --run executes the workflow."""

    exit_code = cli_main(["--run", "run_test_workflow"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Code writing workflow 'run_test_workflow' created in:" in captured.out
    assert "Workflow executed; memory updated at" in captured.out


def test_main_exits_successfully(tmp_path: Path) -> None:
    """The module entrypoint delegates to the CLI and exits cleanly."""

    with pytest.raises(SystemExit) as exc:
        entry_main(["test_exit"])
    assert exc.value.code == 0
