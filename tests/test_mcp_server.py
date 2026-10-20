"""Tests for the MCP server stub (Phase 2 skeleton)."""

import barium.mcp_server


def test_main_exits_zero() -> None:
    """``main()`` returns 0 so the console script exits cleanly."""
    assert barium.mcp_server.main() == 0
