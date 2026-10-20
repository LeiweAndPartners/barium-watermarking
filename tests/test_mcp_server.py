"""Tests for the hand-rolled MCP server: handshake and tools/call via subprocess."""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _send(requests: list[dict[str, object]]) -> list[dict[str, object]]:
    """Send newline-delimited JSON-RPC requests to the server via subprocess
    and return the decoded responses."""
    payload = "\n".join(json.dumps(request) for request in requests) + "\n"
    process = subprocess.run(
        [sys.executable, "-m", "barium.mcp_server"],
        input=payload,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=60,
    )
    assert process.returncode == 0, process.stderr
    return [json.loads(line) for line in process.stdout.splitlines() if line.strip()]


def test_initialize_handshake() -> None:
    """The server answers initialize with its protocol version and info."""
    responses = _send(
        [
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "0"},
                },
            }
        ]
    )
    assert len(responses) == 1
    result = responses[0]["result"]
    assert result["protocolVersion"] == "2024-11-05"
    assert result["serverInfo"]["name"] == "barium"
    assert "tools" in result["capabilities"]


def test_tools_list_exposes_three_tools() -> None:
    """tools/list exposes detect_watermark, generate_key, and selftest."""
    responses = _send(
        [{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}]
    )
    names = {tool["name"] for tool in responses[0]["result"]["tools"]}
    assert names == {"detect_watermark", "generate_key", "selftest"}


def test_tools_call_detect_watermark() -> None:
    """tools/call detect_watermark returns the test statistics."""
    from barium.keygen import generate_key

    key = generate_key()
    responses = _send(
        [
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "detect_watermark",
                    "arguments": {
                        "text": "the time is now for all people",
                        "key": key,
                    },
                },
            }
        ]
    )
    result = responses[0]["result"]
    stats = json.loads(result["content"][0]["text"])
    assert stats["verdict"] in {"watermarked", "not_watermarked", "inconclusive"}
    assert "z_score" in stats
    assert "p_value" in stats


def test_tools_call_generate_key() -> None:
    """tools/call generate_key returns a fresh key."""
    responses = _send(
        [
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "generate_key", "arguments": {}},
            }
        ]
    )
    stats = json.loads(responses[0]["result"]["content"][0]["text"])
    assert "key" in stats


def test_tools_call_selftest() -> None:
    """tools/call selftest returns the round-trip statistics with the demo label."""
    responses = _send(
        [
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {"name": "selftest", "arguments": {"num_tokens": 50}},
            }
        ]
    )
    stats = json.loads(responses[0]["result"]["content"][0]["text"])
    assert "demo" in stats["embedder"]
    assert "not production generation" in stats["embedder"]
    assert "verdict" in stats


def test_tools_call_unknown_tool_is_error() -> None:
    """An unknown tool returns a JSON-RPC error, not a crash."""
    responses = _send(
        [
            {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {"name": "no_such_tool", "arguments": {}},
            }
        ]
    )
    assert responses[0]["error"]["code"] == -32602


def test_notification_produces_no_response() -> None:
    """A notification gets no reply, per JSON-RPC 2.0 section 4.

    Sends notifications/initialized (no id) followed by tools/list (with an
    id): exactly one response line must come back, for the request only.
    """
    payload = (
        json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {},
            }
        )
        + "\n"
        + json.dumps({"jsonrpc": "2.0", "id": 7, "method": "tools/list", "params": {}})
        + "\n"
    )
    process = subprocess.run(
        [sys.executable, "-m", "barium.mcp_server"],
        input=payload,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=60,
    )
    assert process.returncode == 0, process.stderr
    lines = [line for line in process.stdout.splitlines() if line.strip()]
    assert len(lines) == 1
    response = json.loads(lines[0])
    assert response["id"] == 7


def test_tool_descriptions_carry_honesty_framing() -> None:
    """Tool descriptions state the green-list-only framing and the FPR framing."""
    from barium.mcp_server import TOOL_DEFINITIONS

    detect = next(t for t in TOOL_DEFINITIONS if t["name"] == "detect_watermark")
    assert "open green-list scheme only" in detect["description"]
    assert "false-positive rate" in detect["description"]
    selftest = next(t for t in TOOL_DEFINITIONS if t["name"] == "selftest")
    assert "not production generation" in selftest["description"]


def test_no_mcp_sdk_import() -> None:
    """The server imports only from the stdlib and barium."""
    import barium.mcp_server as server_module

    source = open(server_module.__file__, encoding="utf-8").read()
    assert "import mcp" not in source
    assert "from mcp" not in source
