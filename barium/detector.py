"""Green-list watermark detection.

Role: re-derive the green/red vocabulary split from the key, count green
tokens in the text, and compute a one-proportion z-score against the fair-coin
expectation. Implemented in Phase 3; the algorithm spec at
docs/plans/algorithm-spec.md is written before any code lands here.

Honesty framing: the z-score is a false-positive rate, not a certainty
percentage. This detects the open green-list scheme only - not SynthID Text,
whose detector is a trained classifier tied to a private config.
"""

from __future__ import annotations
