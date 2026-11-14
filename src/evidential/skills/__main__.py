"""Print the bundled skill directory: python -m evidential.skills path."""

import argparse
from collections.abc import Sequence

from . import path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m evidential.skills", description="Find the agent skill bundled with Evidential."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("path", help="Print the absolute path to the bundled skill directory.")
    parser.parse_args(argv)
    print(path())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
