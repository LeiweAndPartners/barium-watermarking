"""Tests for the CLI stub (Phase 2 skeleton)."""

import barium.cli


def test_main_exits_zero() -> None:
    """``main()`` returns 0 so the console script exits cleanly."""
    assert barium.cli.main([]) == 0


def test_help_carries_positioning_rule() -> None:
    """The parser description uses the README positioning rule verbatim."""
    parser = barium.cli.build_parser()
    assert (
        "A detection tool for the open green-list scheme — not a SynthID tool."
        in parser.description
    )
