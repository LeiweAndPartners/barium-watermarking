"""barium: a detection tool for the open green-list scheme - not a SynthID tool.

Detects Kirchenbauer-style green-list watermarks (arXiv:2301.10226) with a
one-proportion z-test that needs only the key: no model access, no GPU, no
network calls. Includes a reference demo embedder so the round-trip is
provable without torch, a keygen, a CLI, and a hand-rolled stdio MCP server.

The z-score is a false-positive rate, not a certainty percentage. Short or
low-entropy text carries no signal.
"""

__version__ = "0.1.0"
