"""Test configuration helpers."""

from __future__ import annotations

import pytest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


@pytest.hookimpl
def pytest_addoption(parser: pytest.Parser) -> None:
    """Register coverage related arguments so test runs succeed without pytest-cov."""

    parser.addoption("--cov", action="append", default=[], help="No-op coverage option")
    parser.addoption(
        "--cov-report",
        action="append",
        default=[],
        help="No-op coverage report option",
    )
