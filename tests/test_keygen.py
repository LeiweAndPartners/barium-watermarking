"""Tests for key generation: uniqueness, space, and refusal of defaults."""

import pytest

from barium.keygen import (
    KNOWN_DEFAULT_KEYS,
    MAX_KEY,
    MIN_KEY,
    REFERENCE_DEFAULT_KEY,
    KeyValidationError,
    generate_key,
    validate_key,
)


def test_generate_key_in_documented_space() -> None:
    """Every drawn key lands in [MIN_KEY, MAX_KEY]."""
    for _ in range(100):
        key = generate_key()
        assert MIN_KEY <= key <= MAX_KEY


def test_generate_key_uniqueness_over_repeated_draws() -> None:
    """Repeated draws produce distinct keys - the space is large enough that
    100 draws never collide."""
    keys = {generate_key() for _ in range(100)}
    assert len(keys) == 100


def test_generate_key_never_emits_known_defaults() -> None:
    """The emit path never hands out a known default or shared key."""
    for _ in range(100):
        assert generate_key() not in KNOWN_DEFAULT_KEYS


def test_validate_key_accepts_generated_key() -> None:
    """A generated key passes validation unchanged."""
    key = generate_key()
    assert validate_key(key) == key


def test_validate_key_refuses_reference_default() -> None:
    """The reference implementation's hardcoded key is refused on accept."""
    with pytest.raises(KeyValidationError):
        validate_key(REFERENCE_DEFAULT_KEY)


def test_validate_key_refuses_out_of_space() -> None:
    """Keys outside [MIN_KEY, MAX_KEY] are refused."""
    for bad in (0, -1, MAX_KEY + 1, 2**40):
        with pytest.raises(KeyValidationError):
            validate_key(bad)


def test_validate_key_refuses_non_integer() -> None:
    """Non-integer keys are refused, including bools (a bool is an int)."""
    for bad in ("15485863", 1.5, None, True):
        with pytest.raises(KeyValidationError):
            validate_key(bad)
