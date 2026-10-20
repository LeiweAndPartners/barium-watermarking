"""Command-line interface for barium.

Role: argparse-based entry point exposing ``detect``, ``keygen``, and
``selftest`` subcommands. ``selftest`` ships in Phase 4; ``detect`` and
``keygen`` arrive in Phase 6.

Honesty framing: help text carries the positioning rule - a detection tool for
the open green-list scheme, not a SynthID tool. The selftest output labels the
embedder as a demo.
"""

from __future__ import annotations

import argparse
import sys

from barium.embedder import selftest as run_selftest
from barium.keygen import generate_key


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with the honesty framing in the description."""
    parser = argparse.ArgumentParser(
        prog="barium",
        # The first sentence is the README positioning rule, quoted verbatim
        # (em dash included) so the framing cannot drift between surfaces.
        description=(
            "A detection tool for the open green-list scheme — not a SynthID "
            "tool. Detects Kirchenbauer-style green-list watermarks with a "
            "z-test that needs only the key."
        ),
    )
    subparsers = parser.add_subparsers(dest="command")

    selftest_parser = subparsers.add_parser(
        "selftest",
        help="embed then detect in one command: the round-trip proof",
        description=(
            "Embed a watermarked text with the reference demo embedder "
            "(a labelled demo, not production generation) and detect it "
            "with the z-test."
        ),
    )
    selftest_parser.add_argument(
        "--key",
        type=int,
        default=None,
        help="per-deployment secret key; a fresh key is generated when omitted",
    )
    selftest_parser.add_argument(
        "--tokens",
        type=int,
        default=200,
        help="target length of the embedded text (default: 200)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``barium`` console script."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "selftest":
        key = args.key if args.key is not None else generate_key()
        outcome = run_selftest(key, num_tokens=args.tokens)
        result = outcome["result"]
        print("embedder: demo (reference demo, not production generation)")
        print(f"key: {key}")
        print(f"tokens scored: {result.num_tokens_scored}")
        print(f"green tokens: {result.num_green_tokens}")
        print(f"z-score: {result.z_score:.3f}")
        print(f"verdict: {result.verdict}")
        return 0
    # detect and keygen subcommands arrive in Phase 6.
    parser.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
