"""Tests for the calibration experiment: reproducibility and the power curve."""

import sys
from pathlib import Path

import pytest

# Make the experiments package importable from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from experiments.min_tokens import (  # noqa: E402
    analytic_min_tokens,
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
    undetectable at any realistic length. The measured low-entropy rate in
    docs/min-tokens.md is 0.5025, for which the formula gives ~1.27 million;
    at p = 0.50 exactly the formula diverges entirely.
    """
    near = analytic_min_tokens(green_rate=0.503, z_threshold=4.0, target_tpr=0.95)
    far = analytic_min_tokens(green_rate=1.0, z_threshold=4.0, target_tpr=0.95)
    assert near > 500_000
    assert far < 100


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
