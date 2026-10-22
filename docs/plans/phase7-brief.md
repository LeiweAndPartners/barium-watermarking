# Phase 7 Brief: Docs

*Written by the PM before the phase starts, per `build-plan.md`. Scope: README prose, mermaid diagrams, HTML guides, and the threat model. No code changes.*

## Deliverables

1. README rewritten in the house register: series link, z-test explainer, honesty notes, no-hosting stance, related work, MIT licence
2. Mermaid diagrams: system architecture, detection dataflow, MCP sequence, key lifecycle
3. `docs/guides/*.html`: interactive explainers per `code-standards.md` (self-contained, vanilla JS, one concept per page, worked example with real numbers)
4. `docs/threat-model.md`: the key as attack surface, spoofing and evasion, private mode trade-off, multiple keys with Bonferroni correction
5. Honesty audit passes: no sentence implies SynthID detection; the z-score is described as a false-positive rate, never a certainty; the 25-token caveat is present

## Files in scope

- `README.md`
- `docs/guides/green-list-derivation.html`, `docs/guides/z-test.html`, `docs/guides/key-management.html`, `docs/guides/mcp-protocol.html`
- `docs/threat-model.md`

## Acceptance criteria (binary)

- [ ] README: series link (https://leiwe.partners/insights/eu-ai-act-watermarking), z-test explainer, honesty notes, no-hosting stance, related work (jwkirchenbauer/lm-watermarking, Kirchenbauer et al. 2023, SynthID Text cited as the scheme this tool deliberately does not cover, fortil/watermark-ia-detector-mcp, Sadasivan et al.), MIT licence
- [ ] Every number in the README traces to `post3-plan.md` or `docs/min-tokens.md`
- [ ] Four mermaid diagrams in the safe form: quoted labels, `<br/>` for line breaks, no raw `&`
- [ ] Four HTML guides: self-contained (no CDN, no external fonts, runs from file://), vanilla JS only, one concept per page, worked example with real numbers, links back to the README and the paper
- [ ] `docs/threat-model.md`: the key as attack surface, spoofing (Sadasivan et al. ~1M queries), evasion (paraphrase), private mode trade-off (Kirchenbauer §5), multiple keys with Bonferroni correction
- [ ] Honesty audit: no sentence implies SynthID detection; the z-score is a false-positive rate, never a certainty; the 25-token caveat is present
- [ ] Mermaid diagrams verified in Markdown preview before sign-off
- [ ] pytest green (docs phase must not break the suite)

## Honesty-framing lines that apply

- The positioning rule for all prose: "A detection tool for the open green-list scheme — not a SynthID tool." Never imply it detects SynthID; cite SynthID in related work as the scheme this tool deliberately does not cover, with a pointer to the HF integration for builders who need it.
- The z-score is a false-positive rate, not a certainty percentage. The prosecutor's fallacy applies: P(flag | human) is not P(human | flag).
- The ~25-token caveat: short or low-entropy text carries no signal. The measured minimum (25 scored tokens on high-entropy text) and the low-entropy cap (p collapses to the fair-coin expectation) are the honest numbers.
- Every number in user-facing prose must trace to `post3-plan.md` or `docs/min-tokens.md`.

## Out of scope

Production code changes, experiments, release (Phase 8).
