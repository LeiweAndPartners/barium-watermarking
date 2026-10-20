# Phase 4 Brief: Round-Tip

*Written by the PM before the phase starts, per `build-plan.md`. Scope: the demo embedder, the selftest command, and the round-trip tests. No CLI subcommands beyond selftest, no MCP protocol, no calibration.*

## Deliverables

1. `barium/embedder.py` — demo embedder labelled as a demo in the module docstring and in CLI output; selects tokens biased toward the green list given candidate next-token probabilities
2. `barium selftest` — embed then detect in one command (the CLI gains its first real subcommand)
3. Round-trip tests covering the true-positive, true-negative, and false-negative quadrants, plus the short-text inconclusive criterion

## Files in scope

- `barium/embedder.py`
- `barium/cli.py` (selftest subcommand only)
- `tests/test_embedder.py`, `tests/test_cli.py`

## Acceptance criteria (binary)

- [ ] `barium/embedder.py`: module docstring labels it as a reference demo, not production generation; selects tokens biased toward the green list given candidate next-token probabilities; implements the bias rule from `algorithm-spec.md` (The demo embedder's bias rule)
- [ ] `barium selftest`: embeds then detects in one command; CLI output labels the embedder as a demo
- [ ] Tests (true positive): watermarked round-trip scores above the threshold at T = 200 tokens
- [ ] Tests (true negative): unwatermarked text scores low
- [ ] Tests (false negative): watermarked text evades detection under three attacks — truncation below the minimum length returns an inconclusive verdict; random token substitution (paraphrase stand-in) drops z below the threshold; low-entropy watermarked text carries no signal
- [ ] Tests: short text returns an inconclusive verdict (minimum around 25 tokens of high-entropy text, pending the Phase 5 calibration)
- [ ] Honesty framing: the embedder is labelled a demo everywhere it surfaces; no sentence implies SynthID detection or production generation quality
- [ ] pytest green

## Honesty-framing lines that apply

- The embedder is a labelled reference demo, not production generation. Its docstring and the selftest CLI output must both say so.
- The z-score is a false-positive rate. Test docstrings must not describe a high z as "certain".
- The ~25-token caveat: the short-text test's docstring notes the minimum is pending Phase 5 calibration.
- This detects the open green-list scheme only. No SynthID implication anywhere.

## Out of scope

Calibration experiments and `docs/min-tokens.md` (Phase 5), `detect` and `keygen` CLI subcommands and MCP protocol (Phase 6), README prose (Phase 7).
