"""stdio MCP server for barium, JSON-RPC 2.0 implemented by hand.

Role: expose ``detect_watermark``, ``generate_key``, and ``selftest`` tools
over stdio using only the stdlib - no MCP SDK dependency. The protocol
handling arrives in Phase 6; ``main()`` exists now so the console script
resolves.

Honesty framing: tool descriptions state that detection covers the open
green-list scheme only.
"""

from __future__ import annotations

import sys


def main() -> int:
    """Entry point for the ``barium-mcp`` console script."""
    # Protocol handling arrives in Phase 6; the script must still exit cleanly.
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
