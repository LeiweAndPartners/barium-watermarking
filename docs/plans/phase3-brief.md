# Phase 3 Brief: Core Math

*Written by the PM before the phase starts, per `build-plan.md`. The algorithm spec is written before any implementation. Scope: the detector, the keygen, and their tests. No embedder, no CLI subcommands, no MCP protocol.*

## Deliverables

1. `docs/plans/algorithm-spec.md` — the algorithm specification, written **before** any implementation, extracted from arXiv:2301.10226 §2 and the reference repo (`jwkirchenbauer/lm-watermarking`)
2. `barium/keygen.py` — keys from `secrets`; refuses to emit or accept known default or shared keys; key space documented
3. `barium/detector.py` — `GreenListDetector` and `DetectionResult` dataclass; pure stdlib; tokenisation strategy documented
4. Tests covering the true-negative quadrant, the false-positive rate, and the derivation/uniqueness/refusal criteria below

## Files in scope

- `docs/plans/algorithm-spec.md`
- `barium/keygen.py`, `barium/detector.py`
- `tests/test_keygen.py`, `tests/test_detector.py`

## Acceptance criteria (binary)

- [ ] `algorithm-spec.md` exists and specifies: seed derivation from the previous ngram, hash construction, PRNG choice, green-list size (γ fraction of the vocabulary), the z formula, and the demo embedder's bias rule; the spec cites arXiv:2301.10226 §2 and the specific reference-repo files
- [ ] `barium/keygen.py`: keys drawn from `secrets`; `generate_key()` refuses to emit known default keys (the reference repo's `hash_key` 15485863 among them); a validation function refuses known defaults and shared keys; the key space is documented in the module docstring
- [ ] `barium/detector.py`: `GreenListDetector` class and `DetectionResult` dataclass; imports only from the stdlib; the tokenisation strategy is documented in the module docstring
- [ ] Tests (true negative): unwatermarked text scores below the threshold at every tested length
- [ ] Tests (false-positive rate): Monte Carlo over the null — unwatermarked z-scores match N(0,1) (mean and std within tolerance) and the empirical rate at z = 2 sits in its binomial band. No single-sample assertion at z = 4 (flaky at 3×10⁻⁵); the rate is validated distributionally
- [ ] Tests: green-list derivation reproducible for a fixed key; z-scores match hand-computed values; keygen uniqueness over repeated draws; refusal of defaults
- [ ] Honesty framing: no sentence in code, docstrings, or tests implies SynthID detection; the z-score is described as a false-positive rate; the ~25-token caveat appears where length is discussed
- [ ] pytest green

## Honesty-framing lines that apply

- The z-score is a false-positive rate, not a certainty percentage. Docstrings and comments must not describe z > 4 as "98.4% certain" or similar.
- The ~25-token caveat: short or low-entropy text carries no signal. Where the detector's minimum length is discussed, the caveat is present.
- This detects the open green-list scheme only. No SynthID implication anywhere.

## Out of scope

`barium/embedder.py` logic (Phase 4), `selftest` (Phase 4), calibration experiments (Phase 5), CLI subcommands and MCP protocol (Phase 6), README prose (Phase 7).
