"""Tests for the calibration experiment: reproducibility and the power curve."""

import random
import sys
from pathlib import Path

import pytest

# Make the experiments package importable from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from experiments.min_tokens import (  # noqa: E402
    _watermarked_text,
    analytic_min_tokens,
    measure_low_entropy_green_rate,
    measured_min_tokens,
    sweep,
)
from barium.keygen import generate_key  # noqa: E402


def test_analytic_min_tokens_matches_hand_computed_value() -> None:
    """The power curve matches the hand-computed formula.

    p = 1.0, gamma = 0.5, z_alpha = 4.0, target TPR 0.95 (z_beta = 1.6449):
    T_min = (4.0 + 1.6449)^2 * 0.25 / 0.25 = 5.6449^2 = 31.87
    """
    t_min = analytic_min_tokens(green_rate=1.0, z_threshold=4.0, target_tpr=0.95)
    assert t_min == pytest.approx(31.87, abs=0.05)


def test_analytic_min_tokens_grows_as_p_approaches_gamma() -> None:
    """The minimum explodes as the green rate approaches the fair-coin
    expectation - the low-entropy cap (Appendix G) in formula form.

    p = 0.503 gives T_min = (5.6449)^2 * 0.25 / 0.003^2 = 885,121: effectively
    undetectable at any realistic length. At p = 0.50 exactly the formula
    diverges entirely, which is the low-entropy floor's expected rate.
    """
    near = analytic_min_tokens(green_rate=0.503, z_threshold=4.0, target_tpr=0.95)
    far = analytic_min_tokens(green_rate=1.0, z_threshold=4.0, target_tpr=0.95)
    assert near > 500_000
    assert far < 100


def test_low_entropy_green_rate_is_a_per_key_bernoulli_at_gamma() -> None:
    """The low-entropy floor's green rate is a per-key Bernoulli at gamma.

    With one candidate per position the chain repeats a single bigram, so the
    realised green rate is is_green(token, token) - a per-key constant, 0 or
    1. The fraction of green keys over a large set estimates the Bernoulli's
    mean, gamma. The bound is a deliberate anti-flake margin, not the
    binomial band: over 1,000 keys the sd is about 0.016, so 0.483 (the
    pinned seed's value) sits within 2 sd of 0.5 and the loose 0.35-0.65
    bound exists only so a broken measurement (which would return 0.0, 1.0,
    or a non-Bernoulli rate) cannot pass.
    """
    rate = measure_low_entropy_green_rate()
    assert 0.35 <= rate <= 0.65


def test_sweep_reproduces_measured_minimum_from_fixed_seed() -> None:
    """The reported minimum reproduces from a fixed seed.

    Runs a reduced sweep (the full 1,000-sample sweep takes minutes) over the
    lengths bracketing the measured minimum: the same seed must produce the
    same TPR at each length, and the minimum must land at 25 scored tokens
    as reported in docs/min-tokens.md.
    """
    key = generate_key()
    results = sweep(
        key,
        lengths=(16, 25, 32),
        samples=200,
        z_threshold=4.0,
        seed=42,
    )
    again = sweep(
        key,
        lengths=(16, 25, 32),
        samples=200,
        z_threshold=4.0,
        seed=42,
    )
    assert results == again
    minimum = measured_min_tokens(results, target_tpr=0.95)
    assert minimum == 25


def test_sweep_unwatermarked_arm_stays_below_threshold() -> None:
    """The unwatermarked arm's empirical FPR stays at or below the nominal
    rate at z = 4 (about 3e-5).

    The bound is a deliberate anti-flake margin, not the binomial band: with
    200 samples the expected flag count is 0.0063, so zero flags is the
    expected outcome and the loose 5% bound exists only so a broken null
    (which flags at 50% or more) cannot pass. P(>=1 flag in 200) is about
    0.6%, and even one flag would be an empirical FPR of 0.5%, roughly 160x
    the nominal rate.
    """
    key = generate_key()
    results = sweep(
        key,
        lengths=(50,),
        samples=200,
        z_threshold=4.0,
        seed=7,
    )
    for row in results:
        assert row["fpr"] <= 0.05


def test_watermarked_arm_produces_distinct_samples() -> None:
    """The watermarked arm is a genuine sample, not one text repeated.

    The seeded candidate pool must produce distinct texts across samples:
    a deterministic pool would make the TPR column a single sample repeated
    1,000 times, which is the defect the 0.4 fix removed. Reproducibility
    (same seed, same results) is a separate property and is pinned by
    test_sweep_reproduces_measured_minimum_from_fixed_seed.
    """
    key = generate_key()
    rng = random.Random(42)
    texts = {
        _watermarked_text(key, 26, rng=rng)
        for _ in range(20)
    }
    assert len(texts) == 20
