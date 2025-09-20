"""Console script entry point."""

from __future__ import annotations

import sys
from typing import Sequence

from .cli import main as cli_main


def main(argv: Sequence[str] | None = None) -> None:
    """Delegate execution to the CLI module."""

    exit_code = cli_main(argv)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main(sys.argv[1:])
