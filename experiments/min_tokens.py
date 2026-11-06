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
from barium.embedder import DEMO_WORDS, DemoEmbedder
from barium.keygen import generate_key

# Scored lengths swept by the calibration.
SWEEP_LENGTHS = (10, 16, 25, 32, 50, 64, 100, 128, 200, 400)

# Candidate widths swept by the width calibration: the top-k regime of a
# served model's logprobs, where each position offers only k candidates.
SWEEP_WIDTHS = (2, 3, 4, 5, 8, 10)

# Samples per length per arm (watermarked and unwatermarked).
SAMPLES_PER_ARM = 1_000

# Thresholds: z = 4 (FPR about 3e-5) and z = 2.326 (FPR about 1%).
Z_THRESHOLDS = (4.0, 2.326)

# The calibration pool is the embedder's own word list, so the selftest and
# the tables in docs/min-tokens.md measure the same setting. The tables are
# traced to the current list; a pool edit invalidates them (see DEMO_WORDS).
_WORDS = DEMO_WORDS


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


def _candidate_lists(
    num_tokens: int, rng: random.Random | None = None, width: int | None = None
) -> list[list[tuple[str, float]]]:
    """Build a candidate pool for the demo embed.

    With no rng, every position offers the full word list at near-uniform
    probabilities: the deterministic ceiling case, where the delta boost wins
    every position and the realised green rate is 1.0.

    With an rng, each position offers a random subset of the words at random
    probabilities, the way a model's top-k logprobs behave: some positions
    offer no green candidate, so the realised green rate sits below 1.0 and
    varies per sample. That is what makes the sweep's TPR a rate rather than
    a repeated single sample.
    """
    if rng is None:
        probability = 1.0 / len(_WORDS)
        return [[(word, probability) for word in _WORDS] for _ in range(num_tokens)]
    k = width if width is not None else min(10, len(_WORDS))
    return [
        [(word, rng.random()) for word in rng.sample(_WORDS, k)]
        for _ in range(num_tokens)
    ]


def _watermarked_text(
    key: int, num_tokens: int, rng: random.Random, width: int | None = None
) -> str:
    """Embed a watermarked text of the target length with the demo embedder.

    The candidate pool is drawn from rng, so repeated calls produce different
    texts: the watermarked arm is a genuine sample, not one text repeated.
    The optional width caps how many candidates each position offers, the way
    a model's top-k logprobs behave; the default keeps the calibration's
    10-candidate pool.
    """
    detector = GreenListDetector(key)
    embedder = DemoEmbedder(detector)
    return embedder.embed(_candidate_lists(num_tokens, rng=rng, width=width))


def _unwatermarked_text(num_tokens: int, seed: int) -> str:
    """Build unwatermarked text by sampling filler words with a fixed seed."""
    rng = random.Random(seed)
    return " ".join(rng.choice(_WORDS) for _ in range(num_tokens))


def measure_green_rate(
    key: int, num_tokens: int = 200, width: int | None = None
) -> float:
    """Measure the embedder's realised green rate p on high-entropy text.

    The analytic power curve needs the green rate the embedder actually
    achieves, not the gamma it biases toward: the demo embedder selects the
    highest-boosted candidate, so p sits well above gamma on high-entropy
    pools. The optional width caps how many candidates each position offers,
    the way a model's top-k logprobs behave; the default keeps the
    calibration's 10-candidate pool.
    """
    detector = GreenListDetector(key)
    embedder = DemoEmbedder(detector)
    text = embedder.embed(_candidate_lists(num_tokens, width=width))
    tokens = tokenize(text)
    green = sum(
        1
        for previous, current in zip(tokens, tokens[1:])
        if detector.is_green(previous, current)
    )
    return green / (len(tokens) - 1)


def measure_low_entropy_green_rate(keys: int = 1_000, seed: int = 20_000) -> float:
    """Measure the green rate on the low-entropy floor: one candidate per
    position.

    A single candidate leaves the embedder no choice at any position, so the
    realised green rate is whatever the pool gives — the low-entropy cap
    (Kirchenbauer Appendix G) in its purest form for this embedder. Narrower
    probability distributions do not reach this floor: the delta boost
    dominates any probability split, so a two-candidate pool with a strong
    preference still measures p near 0.75. Only removing the alternatives
    entirely does.

    With one candidate per position the chain repeats a single bigram, so the
    realised green rate is is_green(token, token) — a per-key constant, 0 or
    1, decided by whether that one bigram lands green for the key. The rate
    over a key set is therefore a Bernoulli at gamma: gamma in expectation,
    with no averaging benefit within a single text. This function reports the
    fraction of keys whose chain is green, the empirical estimate of that
    Bernoulli's mean.

    Args:
        keys: Number of keys to average over.
        seed: Seed for the key set, so the rate reproduces.

    Returns:
        The fraction of keys whose single-bigram chain is green.
    """
    green_keys = 0
    for i in range(keys):
        detector = GreenListDetector(seed + i)
        if detector.is_green("token", "token"):
            green_keys += 1
    return green_keys / keys


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
        seed: Seed for both arms, so the sweep reproduces. The watermarked
            arm draws its candidate pools from the same seed, so its TPR is
            an empirical rate over distinct samples rather than one text
            repeated.

    Returns:
        One dict per length: length, watermarked TPR, unwatermarked flag rate.
    """
    detector = GreenListDetector(key, z_threshold=z_threshold)
    results = []
    for length in lengths:
        # The detector scores length - 1 positions; embed one extra token so
        # the scored length matches the sweep target.
        watermarked_rng = random.Random(seed)
        watermarked_flags = 0
        for i in range(samples):
            text = _watermarked_text(key, length + 1, rng=watermarked_rng)
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


def sweep_widths(
    key: int,
    widths: tuple[int, ...] = SWEEP_WIDTHS,
    lengths: tuple[int, ...] = (25, 50, 100, 200),
    samples: int = 100,
    z_threshold: float = 4.0,
    seed: int = 42,
) -> list[dict[str, object]]:
    """Sweep candidate width: TPR per (width, length) pair.

    The watermarked arm draws candidate pools of the given width, so the
    sweep measures how the minimum detectable length depends on candidate
    diversity rather than text length alone. The mechanism under test is
    P(no green candidate at a position) = (1 - gamma)^w: at narrow widths a
    sizeable fraction of positions offers no green candidate, the realised
    green rate collapses toward gamma, and the z-score with it.

    The unwatermarked arm is omitted: the null does not depend on candidate
    width (filler words involve no embedder), and the false-positive rate is
    fixed by the threshold, so the main sweep's null arm already validates
    it.

    Args:
        key: Per-deployment secret key.
        widths: Candidate pool widths to sweep.
        lengths: Scored lengths to sweep.
        samples: Samples per (width, length) cell.
        z_threshold: Verdict threshold.
        seed: Seed for the watermarked arm; each cell derives its own seed
            so every cell reproduces independently of sweep order.

    Returns:
        One dict per cell: width, length, tpr.
    """
    detector = GreenListDetector(key, z_threshold=z_threshold)
    results = []
    for width in widths:
        for length in lengths:
            # Derive a per-cell seed arithmetically: random.Random rejects
            # tuple seeds, and a derived int keeps cells reproducible.
            rng = random.Random(seed * 1_000_003 + width * 10_009 + length)
            flags = 0
            for _ in range(samples):
                text = _watermarked_text(key, length + 1, rng=rng, width=width)
                if detector.detect(text).verdict == "watermarked":
                    flags += 1
            results.append(
                {"width": width, "length": length, "tpr": flags / samples}
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

    print("width sweep at z = 4.0: TPR by candidate width and scored length")
    width_results = sweep_widths(key)
    by_width: dict[int, dict[int, float]] = {}
    for row in width_results:
        by_width.setdefault(int(row["width"]), {})[int(row["length"])] = float(
            row["tpr"]
        )
    swept_lengths = sorted({int(row["length"]) for row in width_results})
    header = " ".join(f"T={n:<3}" for n in swept_lengths)
    print(f"{'width':>5} {header}")
    for width in sorted(by_width):
        cells = " ".join(f"{by_width[width][n]:>5.3f}" for n in swept_lengths)
        print(f"{width:>5} {cells}")
    print()

    low_entropy_rate = measure_low_entropy_green_rate()
    print(f"low-entropy floor (one candidate per position): p = {low_entropy_rate:.4f}")
    print("  (a per-key Bernoulli at gamma: 0 or 1 per key, gamma in expectation;")
    print("   the analytic minimum at p = gamma diverges entirely)")
    print()


if __name__ == "__main__":
    main()
