"""Key generation for green-list watermarks.

Role: emit cryptographically random per-deployment keys from ``secrets`` and
refuse to emit or accept known default or shared keys. Implemented in Phase 3.
"""

from __future__ import annotations
