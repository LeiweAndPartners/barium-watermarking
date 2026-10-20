"""Tests for the embedder stub (Phase 2 skeleton)."""

import barium.embedder


def test_embedder_module_imports() -> None:
    """The embedder module resolves and is labelled as a demo."""
    assert barium.embedder.__doc__ is not None
    assert "demo" in barium.embedder.__doc__
