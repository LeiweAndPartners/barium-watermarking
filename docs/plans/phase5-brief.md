# Phase 5 Brief: Calibration (Minimum Detectable Length)

*Written by the PM before the phase starts, per `build-plan.md`. Scope: the Monte Carlo sweep, the analytic power curve, the results doc, and a reproducibility test. No CLI subcommands, no MCP protocol, no README prose.*

## Deliverables

1. `experiments/min_tokens.py` — Monte Carlo sweep over lengths reporting empirical TPR at fixed FPR, alongside the analytic power curve
2. `docs/min-tokens.md` — the measured minimum for 95% TPR at z = 4 (FPR 3×10⁻⁵) and at FPR ≤ 1% (z = 2.326), plus the high-entropy vs low-entropy comparison; results in tokens and approximate words
3. A reproducibility test — the reported minimum reproduces from a fixed seed

## Files in scope

- `experiments/min_tokens.py`
- `docs/min-tokens.md`
- `tests/test_calibration.py`

## Acceptance criteria (binary)

- [ ] Monte Carlo sweep over lengths T ∈ {10, 16, 25, 32, 50, 64, 100, 128, 200, 400}; for each length, 1,000 watermarked and 1,000 unwatermarked samples; reports empirical TPR at fixed FPR
- [ ] Analytic power curve alongside: `T_min = (z_α + z_β)² γ(1-γ) / (p-γ)²` with the embedder's measured green rate p; the Monte Carlo result must agree with the curve within sampling error
- [ ] `docs/min-tokens.md`: the measured minimum for 95% TPR at z = 4 (FPR 3×10⁻⁵) and at FPR ≤ 1% (z = 2.326), plus the high-entropy vs low-entropy comparison (low-entropy caps p, matching Kirchenbauer Appendix G); results in tokens and approximate words
- [ ] Test: the reported minimum reproduces from a fixed seed
- [ ] Honesty framing: the z-score is a false-positive rate; the ~25-token caveat is contextualised against the measured numbers; no SynthID implication
- [ ] pytest green

## Honesty-framing lines that apply

- The z-score is a false-positive rate, not a certainty. The doc must describe z = 4 as an FPR of about 3×10⁻⁵, never as "98.4% certain".
- The ~25-token caveat: the paper's "as few as 25 tokens" applies to high-entropy text; the measured minimum is the honest number and the doc must say where the paper's claim holds and where it does not.
- Low-entropy caps p (the achievable green rate), matching Kirchenbauer Appendix G. The comparison must state this, not imply low-entropy text is merely "harder".
- This detects the open green-list scheme only. No SynthID implication anywhere.

## Out of scope

`detect` and `keygen` CLI subcommands and MCP protocol (Phase 6), README prose (Phase 7), threat model (Phase 7).
