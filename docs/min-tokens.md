# Minimum Detectable Length

*Calibration results for the barium detector, from `experiments/min_tokens.py`. Every number here traces to experiment output; the watermarked arm is deterministic given the key and the unwatermarked arm is seeded, so the tables reproduce in practice. The z-score is a false-positive rate, not a certainty: a threshold of z = 4 means unwatermarked text exceeds it with probability about 3×10⁻⁵.*

## Setup

The sweep runs 1,000 watermarked and 1,000 unwatermarked samples at each length T ∈ {10, 16, 25, 32, 50, 64, 100, 128, 200, 400} scored tokens, and reports the empirical true-positive rate (TPR) at the threshold. The false-positive rate (FPR) is fixed by the threshold itself, so the unwatermarked arm validates the empirical rate against the nominal one.

Watermarked samples come from the demo embedder over a high-entropy candidate pool (70 common English words per position, near-uniform probabilities). The embedder's measured green rate on this pool is **p = 1.00**: with near-uniform candidates and δ = 2.0, the boosted green candidate wins every position, so every scored token is green. This is the ceiling case — real generation with a language model lands well below it, which is consistent with the paper's empirical detection at 200 tokens being 98.4% rather than 100%.

## The analytic power curve

The one-proportion z-test's power gives the minimum scored length for target TPR 1 − β at threshold z_α:

$$T_{min} = \frac{(z_\alpha + z_\beta)^2 \, \gamma (1 - \gamma)}{(p - \gamma)^2}$$

With γ = 0.5 and the measured p = 1.00:

| Threshold | Nominal FPR | Analytic T_min | Measured T_min (95% TPR) |
|---|---|---|---|
| z = 4.0 | ~3×10⁻⁵ | 31.9 scored tokens | **25 scored tokens** |
| z = 2.326 | ~1% | 15.8 scored tokens | **25 scored tokens** |

The measured minimum at z = 4 (25) sits below the analytic prediction (31.9) for a structural reason, not a sampling one: with p = 1.00 the watermarked z-score is deterministic (z = √T, so z(16) = 4.0 and z(25) = 5.0 exactly), and the power formula's z_β slack models binomial noise around p that is absent at p = 1.00. The formula is therefore a conservative upper bound here, and the agreement with the Monte Carlo curve is directional: raising the threshold raises T_min, and lowering p toward γ makes T_min diverge. The sweep grid contains no length between 16 and 25, so a 31.9 crossing would not be observable on it either.

At z = 2.326 the measured minimum is also 25, and the reason is the detector's operating floor: `DEFAULT_MIN_SCORED_TOKENS = 25` in `barium/detector.py` returns an inconclusive verdict below 25 scored tokens regardless of threshold, so T = 16 scores TPR 0.000 at both thresholds even though the analytic prediction (15.8) sits beneath the floor. The empirical FPR at this threshold lands at 0.8%–1.3% across lengths, consistent with the nominal 1%.

## The sweep at z = 4.0 (FPR ~3×10⁻⁵)

| T (scored tokens) | TPR | Empirical FPR |
|---|---|---|
| 10 | 0.000 | 0.00e+00 |
| 16 | 0.000 | 0.00e+00 |
| 25 | 1.000 | 0.00e+00 |
| 32 | 1.000 | 0.00e+00 |
| 50 | 1.000 | 0.00e+00 |
| 64 | 1.000 | 0.00e+00 |
| 100 | 1.000 | 0.00e+00 |
| 128 | 1.000 | 0.00e+00 |
| 200 | 1.000 | 0.00e+00 |
| 400 | 1.000 | 0.00e+00 |

## The sweep at z = 2.326 (FPR ~1%)

| T (scored tokens) | TPR | Empirical FPR |
|---|---|---|
| 10 | 0.000 | 0.00e+00 |
| 16 | 0.000 | 0.00e+00 |
| 25 | 1.000 | 9.00e-03 |
| 32 | 1.000 | 1.20e-02 |
| 50 | 1.000 | 1.00e-02 |
| 64 | 1.000 | 8.00e-03 |
| 100 | 1.000 | 1.00e-02 |
| 128 | 1.000 | 1.00e-02 |
| 200 | 1.000 | 1.00e-02 |
| 400 | 1.000 | 1.30e-02 |

## High-entropy vs low-entropy

Low entropy caps the achievable green rate p, matching Kirchenbauer Appendix G: when the candidate distribution has little flexibility, the embedder cannot prefer green tokens because there is nothing to prefer between. A two-candidate pool (near-uniform probabilities) measures p = 0.5025 — a hair above the fair-coin expectation. The analytic minimum at that measured rate is **~1.27 million scored tokens at z = 4** and **~631 thousand at z = 2.326**: effectively undetectable at any realistic length. At p = 0.50 exactly the formula diverges entirely.

This is the honest version of the paper's "as few as 25 tokens" claim: it holds for high-entropy text, where the model has real freedom to prefer green tokens. Low-entropy text — prescriptive answers, code, factual completions (the paper's own low-entropy example is code) — carries no reliable signal at any length a detector will see. The detector's inconclusive verdict below 25 scored tokens exists so short texts are reported as "no signal available" rather than flagged.

## In words

- **25 scored tokens** is the measured minimum for 95% TPR at z = 4 (FPR ~3×10⁻⁵) on high-entropy text — **25 words** at barium's whitespace tokenisation (1 token per word in this pool).
- **25 scored tokens** is also the minimum at FPR ≤ 1% (z = 2.326) on the same pool; the looser threshold buys no length reduction here because the signal is already saturated at p = 1.00 and the detector's inconclusive floor sits at 25.
- **Low-entropy text**: no measurable minimum — the green rate collapses to a hair above the fair-coin expectation and the analytic minimum exceeds a million tokens.

## Reproducing

```
.venv/bin/python experiments/min_tokens.py
```

The sweep seeds the unwatermarked arm from a fixed seed; the watermarked arm is deterministic given the key (the demo embedder's selection is deterministic). The reproducibility test in `tests/test_calibration.py` pins the measured minimum from a fixed seed.
