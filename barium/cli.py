"""Command-line interface for barium.

Role: argparse-based entry point exposing ``detect``, ``keygen``, and
``selftest`` subcommands.

Honesty framing: help text carries the positioning rule - a detection tool for
the open green-list scheme, not a SynthID tool. The detect output describes
the z-score as a false-positive rate, never a certainty, and reports an
inconclusive verdict (with the ~25-token caveat) for short texts. The
selftest output labels the embedder as a demo.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from barium.detector import DEFAULT_Z_THRESHOLD, GreenListDetector
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

    detect_parser = subparsers.add_parser(
        "detect",
        help="score a file or inline text for a green-list watermark",
        description=(
            "Score text with the one-proportion z-test. The z-score is a "
            "false-positive rate, not a certainty: z = 4 means unwatermarked "
            "text exceeds it with probability about 3e-5."
        ),
    )
    detect_parser.add_argument(
        "target",
        help="a file path or an inline text string",
    )
    detect_parser.add_argument(
        "--key",
        type=int,
        required=True,
        help="per-deployment secret key used at generation time",
    )
    detect_parser.add_argument(
        "--z-threshold",
        type=float,
        default=DEFAULT_Z_THRESHOLD,
        help=f"verdict threshold (default: {DEFAULT_Z_THRESHOLD})",
    )

    keygen_parser = subparsers.add_parser(
        "keygen",
        help="generate a fresh per-deployment key",
        description=(
            "Generate a cryptographically random key from secrets. Known "
            "default or shared keys are refused."
        ),
    )

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


def _read_target(target: str) -> str:
    """Return the text to score: file contents when the target is a path,
    the target itself otherwise."""
    path = Path(target)
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return target


def _detect(args: argparse.Namespace) -> int:
    """Run the detect subcommand and print the test statistics."""
    detector = GreenListDetector(args.key, z_threshold=args.z_threshold)
    result = detector.detect(_read_target(args.target))
    print(f"key: {args.key}")
    print(f"tokens scored: {result.num_tokens_scored}")
    print(f"green tokens: {result.num_green_tokens}")
    print(f"green fraction: {result.green_fraction:.3f}")
    print(f"z-score: {result.z_score:.3f}")
    print(f"p-value: {result.p_value:.2e}")
    print(f"verdict: {result.verdict}")
    if result.verdict == "inconclusive":
        print(
            "short or low-entropy text carries no signal: the paper's "
            "'as few as 25 tokens' applies to high-entropy text"
        )
    return 0


def _keygen() -> int:
    """Run the keygen subcommand and print a fresh key."""
    print(generate_key())
    return 0


def _selftest(args: argparse.Namespace) -> int:
    """Run the selftest subcommand and print the round-trip statistics."""
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


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``barium`` console script."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "detect":
        return _detect(args)
    if args.command == "keygen":
        return _keygen()
    if args.command == "selftest":
        return _selftest(args)
    parser.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
