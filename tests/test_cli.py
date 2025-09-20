"""CLI behaviour tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from mcp_workflows.cli import build_demo_workflow, main as cli_main
from mcp_workflows.main import main as entry_main


def test_build_demo_workflow_creates_yaml(tmp_path: Path) -> None:
    """The demo builder writes a YAML file to the requested location."""

    output_path = tmp_path / "demo.yaml"
    memory_path = tmp_path / "memory.md"
    build_demo_workflow(
        goal="Prove the builder works",
        output_path=output_path,
        memory_file=memory_path,
    )
    assert output_path.exists()
    text = output_path.read_text(encoding="utf-8")
    assert "goal" in text
    assert "tasks" in text


def test_cli_main_reports_destination(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Invoking the CLI entry prints the destination path."""

    output_path = tmp_path / "cli.yaml"
    memory_path = tmp_path / "cli_memory.md"
    exit_code = cli_main(
        ["--goal", "Check CLI", "--out", str(output_path), "--memory", str(memory_path)]
    )
    assert exit_code == 0
    captured = capsys.readouterr()
    assert str(output_path) in captured.out
    assert output_path.exists()
    assert not memory_path.exists()


def test_cli_main_run_executes_workflow(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Running the CLI updates the requested memory file."""

    output_path = tmp_path / "run.yaml"
    memory_path = tmp_path / "memory.md"
    exit_code = cli_main(
        [
            "--goal",
            "Exercise run mode",
            "--out",
            str(output_path),
            "--memory",
            str(memory_path),
            "--run",
        ]
    )
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Workflow executed" in captured.out
    assert memory_path.exists()
    content = memory_path.read_text(encoding="utf-8")
    assert "Demo Plan" in content


def test_main_exits_successfully(tmp_path: Path) -> None:
    """The module entrypoint delegates to the CLI and exits cleanly."""

    with pytest.raises(SystemExit) as exc:
        entry_main(["--out", str(tmp_path / "entry.yaml"), "--memory", str(tmp_path / "memo.md")])
    assert exc.value.code == 0


