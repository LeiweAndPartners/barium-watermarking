"""Key generation for green-list watermarks.

Role: emit cryptographically random per-deployment keys from ``secrets`` and
refuse to emit or accept known default or shared keys.

Key space: integers in [1, 2**31 - 1], drawn with ``secrets.randbits(31)``.
The space is large enough that accidental collision between deployments is
negligible and small enough that keys stay readable in configuration. The
reference implementation's default hash key (15485863, from
``jwkirchenbauer/lm-watermarking`` ``watermark_processor.py``) is refused on
both the emit and the accept path: a key that ships in a public repository is
not a secret, and a split derived from it is predictable.
"""

from __future__ import annotations

import secrets

# The reference implementation's hardcoded hash key. Refused everywhere: a
# default key is public knowledge, so a split derived from it is predictable.
REFERENCE_DEFAULT_KEY = 15485863

# Known shared defaults refused on emit and accept. Extend only with keys that
# are publicly documented defaults of other implementations.
KNOWN_DEFAULT_KEYS: frozenset[int] = frozenset({REFERENCE_DEFAULT_KEY})

# Documented key space: [MIN_KEY, MAX_KEY]. 0 is excluded so a key is always
# truthy and a missing key cannot masquerade as a valid one.
MIN_KEY = 1
MAX_KEY = 2**31 - 1


class KeyValidationError(ValueError):
    """Raised when a key is outside the documented space or a known default."""


def generate_key() -> int:
    """Return a cryptographically random key from the documented space.

    Draws from ``secrets`` (never ``random``) and redraws on the vanishingly
    rare case of landing on a known default, so the emit path never hands out
    a publicly predictable key.

    Returns:
        An integer key in [MIN_KEY, MAX_KEY], not in KNOWN_DEFAULT_KEYS.
    """
    while True:
        key = secrets.randbits(31)
        if key >= MIN_KEY and key not in KNOWN_DEFAULT_KEYS:
            return key


def validate_key(key: int) -> int:
    """Validate a key against the documented space and known defaults.

    Args:
        key: The candidate key.

    Returns:
        The key, unchanged, when valid.

    Raises:
        KeyValidationError: When the key is outside [MIN_KEY, MAX_KEY] or is
            a known default or shared key.
    """
    if not isinstance(key, int) or isinstance(key, bool):
        raise KeyValidationError("key must be an integer")
    if key < MIN_KEY or key > MAX_KEY:
        raise KeyValidationError(
            f"key must be in [{MIN_KEY}, {MAX_KEY}], got {key}"
        )
    if key in KNOWN_DEFAULT_KEYS:
        raise KeyValidationError(
            "key is a known default or shared key and is refused"
        )
    return key
