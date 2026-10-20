"""stdio MCP server for barium, JSON-RPC 2.0 implemented by hand.

Role: expose ``detect_watermark``, ``generate_key``, and ``selftest`` tools
over stdio using only the stdlib - no MCP SDK dependency. The protocol is
implemented directly: newline-delimited JSON-RPC 2.0 requests in, responses
out, with ``initialize``, ``tools/list``, and ``tools/call`` handled per the
MCP specification's stdio transport.

Honesty framing: tool descriptions state that detection covers the open
green-list scheme only, and that the z-score is a false-positive rate.
"""

from __future__ import annotations

import json
import sys

from barium import __version__
from barium.detector import DEFAULT_Z_THRESHOLD, GreenListDetector
from barium.embedder import selftest as run_selftest
from barium.keygen import generate_key

PROTOCOL_VERSION = "2024-11-05"

TOOL_DEFINITIONS = [
    {
        "name": "detect_watermark",
        "description": (
            "Score text for a Kirchenbauer-style green-list watermark with a "
            "one-proportion z-test. Detects the open green-list scheme only - "
            "not SynthID Text. The z-score is a false-positive rate, not a "
            "certainty: z = 4 means unwatermarked text exceeds it with "
            "probability about 3e-5."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The text to score."},
                "key": {"type": "integer", "description": "The per-deployment secret key."},
                "z_threshold": {
                    "type": "number",
                    "description": "Verdict threshold (default 4.0).",
                },
            },
            "required": ["text", "key"],
        },
    },
    {
        "name": "generate_key",
        "description": (
            "Generate a cryptographically random per-deployment key from "
            "secrets. Known default or shared keys are refused."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "selftest",
        "description": (
            "Embed a watermarked text with the reference demo embedder (a "
            "labelled demo, not production generation) and detect it with "
            "the z-test: the round-trip proof."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "key": {"type": "integer", "description": "Optional key; a fresh key is generated when omitted."},
                "num_tokens": {"type": "integer", "description": "Target length of the embedded text (default 200)."},
            },
        },
    },
]


def _tool_detect_watermark(arguments: dict[str, object]) -> dict[str, object]:
    """Run the detect tool and return the test statistics."""
    text = arguments["text"]
    key = arguments["key"]
    if not isinstance(text, str):
        raise ValueError("text must be a string")
    if not isinstance(key, int) or isinstance(key, bool):
        raise ValueError("key must be an integer")
    z_threshold = arguments.get("z_threshold", DEFAULT_Z_THRESHOLD)
    detector = GreenListDetector(key, z_threshold=float(z_threshold))
    result = detector.detect(text)
    return {
        "num_tokens_scored": result.num_tokens_scored,
        "num_green_tokens": result.num_green_tokens,
        "green_fraction": result.green_fraction,
        "z_score": result.z_score,
        "p_value": result.p_value,
        "z_threshold": result.z_threshold,
        "verdict": result.verdict,
    }


def _tool_generate_key(arguments: dict[str, object]) -> dict[str, object]:
    """Run the keygen tool."""
    return {"key": generate_key()}


def _tool_selftest(arguments: dict[str, object]) -> dict[str, object]:
    """Run the selftest tool."""
    key = arguments.get("key")
    num_tokens = arguments.get("num_tokens", 200)
    outcome = run_selftest(
        int(key) if key is not None else generate_key(),
        num_tokens=int(num_tokens),
    )
    result = outcome["result"]
    return {
        "embedder": "demo (reference demo, not production generation)",
        "num_tokens_scored": result.num_tokens_scored,
        "num_green_tokens": result.num_green_tokens,
        "z_score": result.z_score,
        "verdict": result.verdict,
    }


TOOL_HANDLERS = {
    "detect_watermark": _tool_detect_watermark,
    "generate_key": _tool_generate_key,
    "selftest": _tool_selftest,
}


def handle_request(request: dict[str, object]) -> dict[str, object] | None:
    """Handle one JSON-RPC 2.0 request and return the response.

    Notifications (requests without an id) produce no response, per JSON-RPC
    2.0 section 4: the server must not reply to a notification regardless of
    method.

    Args:
        request: The decoded JSON-RPC request object.

    Returns:
        The response object, or None for notifications.
    """
    request_id = request.get("id")
    method = request.get("method")
    params = request.get("params") or {}

    if request_id is None:
        # A notification: no reply, whatever the method.
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "barium", "version": __version__},
            },
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": TOOL_DEFINITIONS},
        }

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}
        handler = TOOL_HANDLERS.get(name)
        if handler is None:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": f"unknown tool: {name}"},
            }
        try:
            result = handler(arguments)
        except (KeyError, TypeError, ValueError) as error:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": f"error: {error}"}],
                    "isError": True,
                },
            }
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result)}],
            },
        }

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": f"method not found: {method}"},
    }


def serve() -> None:
    """Read newline-delimited JSON-RPC requests from stdin and write
    responses to stdout until stdin closes."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "parse error"},
            }
        else:
            response = handle_request(request)
        if response is not None:
            print(json.dumps(response), flush=True)


def main() -> int:
    """Entry point for the ``barium-mcp`` console script."""
    serve()
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
