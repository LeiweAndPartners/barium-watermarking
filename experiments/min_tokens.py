"""Minimum detectable length: Monte Carlo sweep and analytic power curve.

Role: measure the shortest text the detector flags reliably, and check the
measurement against the analytic power curve. The sweep runs 1,000 watermarked
and 1,000 unwatermarked samples per length and reports empirical TPR at fixed
FPR; the analytic curve predicts the same quantity from the embedder's
measured green rate.

The analytic minimum follows from the one-proportion z-test's power (the z
statistic is arXiv:2301.10226 §2; the inversion is the standard one-proportion
power formula): a watermarked text with green rate p reaches TPR 1 - beta at
threshold z_alpha when

    T_min = (z_alpha + z_beta)^2 * gamma * (1 - gamma) / (p - gamma)^2

Run as a script: .venv/bin/python experiments/min_tokens.py

Honesty framing: the z-score is a false-positive rate, not a certainty. A
threshold of z = 4 means unwatermarked text exceeds it with probability about
3e-5. The paper's "as few as 25 tokens" claim applies to high-entropy text;
low-entropy text caps the achievable green rate p (Kirchenbauer Appendix G),
which is why the low-entropy minimum is reported separately.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

# Allow running as a script from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from barium.detector import GreenListDetector, tokenize
from barium.embedder import DemoEmbedder
from barium.keygen import generate_key

# Sweep lengths from the build plan.
SWEEP_LENGTHS = (10, 16, 25, 32, 50, 64, 100, 128, 200, 400)

# Samples per length per arm (watermarked and unwatermarked).
SAMPLES_PER_ARM = 1_000

# Thresholds: z = 4 (FPR about 3e-5) and z = 2.326 (FPR about 1%).
Z_THRESHOLDS = (4.0, 2.326)

_WORDS = (
    "time year people way day man thing woman life child world school state "
    "family student group country problem hand part place case week company "
    "system program question work government number night point home water "
    "room mother area money story fact month lot right study book eye job "
    "word business issue side kind head house service friend father power "
    "hour game line end member law car city community name president team"
).split()


def _normal_sf(z: float) -> float:
    """Standard-normal upper tail, the false-positive rate at threshold z."""
    return math.erfc(z / math.sqrt(2.0)) / 2.0


def _normal_isf(p: float) -> float:
    """Inverse of the standard-normal upper tail: the z at false-positive p."""
    lo, hi = -10.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if _normal_sf(mid) > p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def _candidate_lists(num_tokens: int) -> list[list[tuple[str, float]]]:
    """High-entropy candidate pool with near-uniform probabilities."""
    probability = 1.0 / len(_WORDS)
    return [[(word, probability) for word in _WORDS] for _ in range(num_tokens)]


def _watermarked_text(key: int, num_tokens: int) -> str:
    """Embed a watermarked text of the target length with the demo embedder."""
    detector = GreenListDetector(key)
    embedder = DemoEmbedder(detector)
    return embedder.embed(_candidate_lists(num_tokens))


def _unwatermarked_text(num_tokens: int, seed: int) -> str:
    """Build unwatermarked text by sampling filler words with a fixed seed."""
    rng = random.Random(seed)
    return " ".join(rng.choice(_WORDS) for _ in range(num_tokens))


def measure_green_rate(key: int, num_tokens: int = 200) -> float:
    """Measure the embedder's realised green rate p on high-entropy text.

    The analytic power curve needs the green rate the embedder actually
    achieves, not the gamma it biases toward: the demo embedder selects the
    highest-boosted candidate, so p sits well above gamma on high-entropy
    pools.
    """
    detector = GreenListDetector(key)
    embedder = DemoEmbedder(detector)
    text = embedder.embed(_candidate_lists(num_tokens))
    tokens = tokenize(text)
    green = sum(
        1
        for previous, current in zip(tokens, tokens[1:])
        if detector.is_green(previous, current)
    )
    return green / (len(tokens) - 1)


def analytic_min_tokens(
    green_rate: float,
    z_threshold: float,
    target_tpr: float,
    gamma: float = 0.5,
) -> float:
    """Return the analytic minimum scored length for the target TPR.

    T_min = (z_alpha + z_beta)^2 * gamma * (1 - gamma) / (p - gamma)^2, where
    z_alpha is the threshold (its false-positive rate is the alpha) and
    z_beta is the standard-normal quantile at the miss rate 1 - target_tpr.
    """
    z_beta = _normal_isf(1.0 - target_tpr)
    numerator = (z_threshold + z_beta) ** 2 * gamma * (1.0 - gamma)
    denominator = (green_rate - gamma) ** 2
    return numerator / denominator


def sweep(
    key: int,
    lengths: tuple[int, ...] = SWEEP_LENGTHS,
    samples: int = SAMPLES_PER_ARM,
    z_threshold: float = 4.0,
    seed: int = 0,
) -> list[dict[str, object]]:
    """Run the Monte Carlo sweep and return per-length results.

    For each length, samples watermarked and unwatermarked texts, scores them
    with the detector, and reports the empirical TPR at the threshold. The
    FPR is fixed by the threshold itself (about 3e-5 at z = 4), so the
    unwatermarked arm validates that the empirical false-positive rate stays
    at or below the threshold's nominal rate.

    Args:
        key: Per-deployment secret key.
        lengths: Scored lengths to sweep.
        samples: Samples per arm per length.
        z_threshold: Verdict threshold.
        seed: Seed for the unwatermarked arm, so the sweep reproduces.

    Returns:
        One dict per length: length, watermarked TPR, unwatermarked flag rate.
    """
    detector = GreenListDetector(key, z_threshold=z_threshold)
    results = []
    for length in lengths:
        # The detector scores length - 1 positions; embed one extra token so
        # the scored length matches the sweep target.
        watermarked_flags = 0
        for i in range(samples):
            text = _watermarked_text(key, length + 1)
            if detector.detect(text).verdict == "watermarked":
                watermarked_flags += 1

        unwatermarked_flags = 0
        for i in range(samples):
            text = _unwatermarked_text(length + 1, seed=seed + i)
            if detector.detect(text).verdict == "watermarked":
                unwatermarked_flags += 1

        results.append(
            {
                "length": length,
                "tpr": watermarked_flags / samples,
                "fpr": unwatermarked_flags / samples,
            }
        )
    return results


def measured_min_tokens(
    results: list[dict[str, object]],
    target_tpr: float = 0.95,
) -> int | None:
    """Return the shortest swept length reaching the target TPR, or None."""
    for row in results:
        if row["tpr"] >= target_tpr:
            return int(row["length"])
    return None


def main() -> None:
    """Run the sweep, print the table, and compare against the power curve."""
    key = generate_key()
    green_rate = measure_green_rate(key)
    print(f"measured green rate p = {green_rate:.3f} (gamma = 0.5)")
    print()
    for z_threshold in Z_THRESHOLDS:
        nominal_fpr = _normal_sf(z_threshold)
        print(f"threshold z = {z_threshold} (nominal FPR {nominal_fpr:.2e})")
        results = sweep(key, z_threshold=z_threshold)
        minimum = measured_min_tokens(results)
        analytic = analytic_min_tokens(green_rate, z_threshold, target_tpr=0.95)
        print(f"{'T':>5} {'TPR':>8} {'FPR':>10}")
        for row in results:
            print(f"{row['length']:>5} {row['tpr']:>8.3f} {row['fpr']:>10.2e}")
        print(f"measured min for 95% TPR: {minimum}")
        print(f"analytic min: {analytic:.1f}")
        print()


if __name__ == "__main__":
    main()
