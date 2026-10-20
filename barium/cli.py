"""Command-line interface for barium.

Role: argparse-based entry point exposing ``detect``, ``keygen``, and
``selftest`` subcommands. Surfaces arrive in Phase 6; ``main()`` exists now so
the console script resolves and ``barium --help`` works.

Honesty framing: help text carries the positioning rule - a detection tool for
the open green-list scheme, not a SynthID tool.
"""

from __future__ import annotations

import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with the honesty framing in the description."""
    return argparse.ArgumentParser(
        prog="barium",
        # The first sentence is the README positioning rule, quoted verbatim
        # (em dash included) so the framing cannot drift between surfaces.
        description=(
            "A detection tool for the open green-list scheme — not a SynthID "
            "tool. Detects Kirchenbauer-style green-list watermarks with a "
            "z-test that needs only the key."
        ),
    )


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``barium`` console script."""
    parser = build_parser()
    args = parser.parse_args(argv)
    # Subcommands arrive in Phase 6; until then the parser only answers --help.
    parser.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
