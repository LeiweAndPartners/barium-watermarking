"""Tests for the detector stub (Phase 2 skeleton)."""

import barium.detector


def test_detector_module_imports() -> None:
    """The detector module resolves and carries its honesty framing."""
    assert barium.detector.__doc__ is not None
    assert "false-positive rate" in barium.detector.__doc__
