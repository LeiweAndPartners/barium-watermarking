# Phase 6 Brief: Surfaces

*Written by the PM before the phase starts, per `build-plan.md`. Scope: the full CLI surface and the hand-rolled MCP server, plus their tests. No README prose, no docs.*

## Deliverables

1. `barium/cli.py` — the full argparse surface: `barium detect <file-or-text> --key <int>`, `barium keygen`, `barium selftest`; help text carries the honesty framing
2. `barium/mcp_server.py` — stdio MCP server, JSON-RPC 2.0 implemented by hand with the stdlib (no MCP SDK); tools `detect_watermark(text, key, z_threshold?)`, `generate_key()`, `selftest()`
3. Surface tests — CLI smoke tests; MCP handshake and `tools/call` via subprocess

## Files in scope

- `barium/cli.py`, `barium/mcp_server.py`
- `tests/test_cli.py`, `tests/test_mcp_server.py`

## Acceptance criteria (binary)

- [ ] CLI: `barium detect <file-or-text> --key <int>` scores a file or inline text and prints the test statistics; `barium keygen` prints a fresh key; `barium selftest` embeds then detects; help text carries the positioning rule verbatim
- [ ] MCP server: stdio, JSON-RPC 2.0 by hand with the stdlib (no MCP SDK import anywhere); implements `initialize`, `tools/list`, and `tools/call`; tools `detect_watermark(text, key, z_threshold?)`, `generate_key()`, `selftest()`
- [ ] Tests: CLI smoke tests for each subcommand; MCP handshake and `tools/call` via subprocess
- [ ] Honesty framing: CLI help and MCP tool descriptions state the positioning rule and the false-positive-rate framing; no SynthID implication
- [ ] pytest green

## Honesty-framing lines that apply

- The CLI help description uses the README positioning rule verbatim: "A detection tool for the open green-list scheme — not a SynthID tool."
- The `detect` output describes the z-score as a false-positive rate, never a certainty.
- MCP tool descriptions state that detection covers the open green-list scheme only.
- The ~25-token caveat appears in the detect output for inconclusive verdicts.

## Out of scope

README prose, mermaid diagrams, HTML guides, threat model (Phase 7). Release (Phase 8).
