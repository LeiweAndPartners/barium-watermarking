"""Tests for the CLI: help framing and the selftest subcommand."""

import barium.cli


def test_main_exits_zero_without_subcommand() -> None:
    """``main()`` returns 0 so the console script exits cleanly."""
    assert barium.cli.main([]) == 0


def test_help_carries_positioning_rule() -> None:
    """The parser description uses the README positioning rule verbatim."""
    parser = barium.cli.build_parser()
    assert (
        "A detection tool for the open green-list scheme — not a SynthID tool."
        in parser.description
    )


def test_selftest_subcommand_exits_zero(capsys) -> None:
    """``barium selftest`` embeds then detects in one command."""
    exit_code = barium.cli.main(["selftest", "--tokens", "50"])
    assert exit_code == 0
    output = capsys.readouterr().out
    assert "verdict:" in output
    assert "z-score:" in output


def test_selftest_output_labels_embedder_demo(capsys) -> None:
    """The selftest CLI output labels the embedder as a demo."""
    barium.cli.main(["selftest", "--tokens", "50"])
    output = capsys.readouterr().out
    assert "demo" in output
    assert "not production generation" in output


def test_selftest_with_explicit_key(capsys) -> None:
    """An explicit key is used and echoed in the output."""
    from barium.keygen import generate_key

    key = generate_key()
    barium.cli.main(["selftest", "--key", str(key), "--tokens", "50"])
    output = capsys.readouterr().out
    assert f"key: {key}" in output
