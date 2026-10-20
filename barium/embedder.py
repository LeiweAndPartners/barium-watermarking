"""Reference demo embedder.

Role: select tokens biased toward the green list given candidate next-token
probabilities, so the embed-then-detect round-trip is provable without torch.

Honesty framing: this is a labelled reference demo, not production generation.
It does not ship a language model and makes no claim to generation quality.
"""

from __future__ import annotations
