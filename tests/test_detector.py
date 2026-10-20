"""Tests for the green-list detector.

Covers the true-negative quadrant, the false-positive rate (Monte Carlo over
the null, validated distributionally), derivation reproducibility, and
hand-computed z values. No single-sample assertion at z = 4: that rate is
about 3e-5, so a single draw would be flaky.
"""

import math
import random

import pytest

from barium.detector import (
    DEFAULT_MIN_SCORED_TOKENS,
    INCONCLUSIVE,
    NOT_WATERMARKED,
    GreenListDetector,
    DetectionResult,
    tokenize,
)
from barium.keygen import generate_key

# High-entropy filler: common English words with no repeated structure, so the
# null behaves like the paper's unwatermarked baseline.
_WORDS = (
    "time year people way day man thing woman life child world school state "
    "family student group country problem hand part place case week company "
    "system program question work government number night point home water "
    "room mother area money story fact month lot right study book eye job "
    "word business issue side kind head house service friend father power "
    "hour game line end member law car city community name president team "
    "minute idea kid body information back parent face others level office "
    "health person art war history party result change morning reason "
    "research girl guy moment air teacher force education"
).split()


def _unwatermarked_text(num_tokens: int, seed: int) -> str:
    """Build unwatermarked text by sampling filler words with a fixed seed."""
    rng = random.Random(seed)
    return " ".join(rng.choice(_WORDS) for _ in range(num_tokens))


def test_tokenize_deterministic_and_strips_punctuation() -> None:
    """Tokenisation is deterministic and strips leading/trailing punctuation."""
    text = "Hello, world! The TIME; is 'now'."
    tokens = tokenize(text)
    assert tokens == ["hello", "world", "the", "time", "is", "now"]
    assert tokenize(text) == tokens


def test_green_list_reproducible_for_fixed_key() -> None:
    """The same key and previous token always re-derive the same green list."""
    key = generate_key()
    detector = GreenListDetector(key)
    first = detector.green_list("time")
    second = GreenListDetector(key).green_list("time")
    assert first == second


def test_green_list_differs_across_keys() -> None:
    """Different keys produce unrelated splits for the same previous token."""
    first = GreenListDetector(generate_key()).green_list("time")
    second = GreenListDetector(generate_key()).green_list("time")
    assert first != second


def test_green_list_size_is_gamma_fraction() -> None:
    """The green list holds floor(gamma * vocab_size) entries."""
    detector = GreenListDetector(generate_key(), gamma=0.5)
    assert len(detector.green_list("time")) == 25_000


def test_z_score_matches_hand_computed_value() -> None:
    """The z statistic matches the hand-computed one-proportion formula.

    G = 18 green of T = 20 scored at gamma = 0.5:
    z = (18 - 10) / sqrt(20 * 0.5 * 0.5) = 8 / sqrt(5) = 3.5777...
    """
    detector = GreenListDetector(generate_key())
    z = detector._z_score(18, 20)
    assert z == pytest.approx(8.0 / math.sqrt(5.0))


def test_z_score_zero_when_at_expectation() -> None:
    """A green count exactly at the fair-coin expectation scores z = 0."""
    detector = GreenListDetector(generate_key())
    assert detector._z_score(10, 20) == pytest.approx(0.0)


def test_true_negative_below_threshold_at_every_tested_length() -> None:
    """Unwatermarked text scores below the threshold at every tested length."""
    detector = GreenListDetector(generate_key())
    for length in (30, 50, 100, 200, 400):
        result = detector.detect(_unwatermarked_text(length, seed=length))
        assert result.verdict == NOT_WATERMARKED
        assert result.z_score <= detector.z_threshold


def test_false_positive_rate_matches_null_distribution() -> None:
    """Monte Carlo over the null: unwatermarked z-scores match N(0, 1).

    With 2,000 draws the mean's standard error is about 0.022 and the std's
    is about 0.016, so tolerances of 0.15 and 0.15 sit well inside sampling
    error while still catching a broken construction.
    """
    detector = GreenListDetector(generate_key(), min_scored_tokens=50)
    z_scores = []
    for i in range(2_000):
        result = detector.detect(_unwatermarked_text(51, seed=10_000 + i))
        z_scores.append(result.z_score)

    mean = sum(z_scores) / len(z_scores)
    variance = sum((z - mean) ** 2 for z in z_scores) / len(z_scores)
    std = math.sqrt(variance)
    assert mean == pytest.approx(0.0, abs=0.15)
    assert std == pytest.approx(1.0, abs=0.15)


def test_false_positive_rate_at_z2_sits_in_binomial_band() -> None:
    """The empirical rate at z = 2 sits inside its binomial band.

    Under the null, P(z > 2) is about 0.0228. With 2,000 draws the expected
    count is about 45.6 with standard deviation about 6.7, so the band
    [expected - 4sd, expected + 4sd] is roughly [19, 72] - wide enough to be
    stable across runs, tight enough to catch a broken null.
    """
    detector = GreenListDetector(generate_key(), min_scored_tokens=50)
    exceedances = 0
    trials = 2_000
    for i in range(trials):
        result = detector.detect(_unwatermarked_text(51, seed=50_000 + i))
        if result.z_score > 2.0:
            exceedances += 1

    expected = trials * 0.0228
    sd = math.sqrt(trials * 0.0228 * (1 - 0.0228))
    assert expected - 4 * sd <= exceedances <= expected + 4 * sd


def test_short_text_returns_inconclusive() -> None:
    """Text below the minimum scored length is inconclusive, not flagged."""
    detector = GreenListDetector(generate_key())
    result = detector.detect(_unwatermarked_text(20, seed=1))
    assert result.verdict == INCONCLUSIVE
    assert result.num_tokens_scored == 19
    assert result.num_tokens_scored < DEFAULT_MIN_SCORED_TOKENS


def test_detection_result_is_dataclass() -> None:
    """DetectionResult is a frozen dataclass carrying the test statistics."""
    detector = GreenListDetector(generate_key(), min_scored_tokens=10)
    result = detector.detect(_unwatermarked_text(60, seed=2))
    assert isinstance(result, DetectionResult)
    assert result.num_green_tokens <= result.num_tokens_scored
    assert 0.0 <= result.green_fraction <= 1.0
    assert 0.0 <= result.p_value <= 1.0


def test_detector_refuses_default_key() -> None:
    """The detector validates its key through barium.keygen."""
    from barium.keygen import KeyValidationError, REFERENCE_DEFAULT_KEY

    with pytest.raises(KeyValidationError):
        GreenListDetector(REFERENCE_DEFAULT_KEY)


def test_module_docstring_carries_honesty_framing() -> None:
    """The module docstring states the false-positive-rate framing."""
    import barium.detector as detector_module

    assert detector_module.__doc__ is not None
    assert "false-positive rate" in detector_module.__doc__
