# barium-watermarking

*Standalone workspace at `~/GitHubRepos/barium-watermarking` (sibling of watermark-demo) — the build happens in a separate VS Code window and chat set opened at this folder. This README is the project brief; the planning documents in `docs/plans/` were copied from the watermark-demo workspace so the new window has full context.*

## What this will be

A standalone, local-first, zero-hosting toolkit for Kirchenbauer-style green-list LLM watermark detection and reference embedding, published by [Leiwe & Partners](https://github.com/LeiweAndPartners) as a community companion to their EU AI Act watermarking blog series.

- **Repo**: `LeiweAndPartners/barium-watermarking` (GitHub org)
- **PyPI name**: `barium-watermarking` (verified free, 2026-10-20)
- **Name rationale**: the canary-trap lineage — MI5's "barium meal test" (per Peter Wright's *Spycatcher*), coined as "canary trap" by Tom Clancy in *Patriot Games* (1987). Per-copy document fingerprinting is the direct ancestor of text watermarking; the post 3 history section tells this story. The gerund "watermarking" (not "-embedder") because the toolkit does both halves: detection is the primary deliverable, the embedder is a reference demo.
- **No hosting**: CLI + MCP server, everything runs on the user's machine. No GPU, no model weights, no network calls. Text never leaves the user's perimeter.

## Scope (detection primary + reference embedder)

**Detection is the primary deliverable** — it's the deployable, zero-cost half (the z-test needs no model access, so it runs anywhere). The embedder exists so the round-trip is provable without torch; it is a reference demo, not production generation.

1. **Detector** — green-list z-score detection per Kirchenbauer et al. 2023 ([arXiv:2301.10226](https://arxiv.org/abs/2301.10226)): hash of the previous ngram seeds a pseudo-random green/red vocabulary split; detection counts green tokens and computes a one-proportion z-score against the fair-coin expectation (γ = 0.5). z > 4 → false-positive rate ~3×10⁻⁵. **No model access needed — just the key.** Pure Python, stdlib only.
2. **Reference embedder** — a minimal, clearly-labelled demo embedder (bias token selection toward the green list given candidate next-token probabilities) so the round-trip works without torch. Not production generation.
3. **Keygen** — cryptographically random per-deployment keys. Must refuse to emit shared/default keys (no hardcoded keys anywhere).
4. **CLI** (argparse, no heavy deps): `barium detect <file-or-text> --key <int>`, `barium keygen`, `barium selftest` (embed → detect round-trip).
5. **MCP server** — stdio, JSON-RPC 2.0 implemented by hand with the stdlib (no MCP SDK dependency). Tools: `detect_watermark(text, key, z_threshold?)`, `generate_key()`, `selftest()`.
6. **Tests** — the full confusion matrix: true positive (round-trip embed → detect → high z), true negative (unwatermarked text → low z), false-positive rate (Monte Carlo over the null distribution; expected ~3×10⁻⁵ at z=4, validated distributionally rather than by single-sample assertion), false negative (truncation below minimum length, token-substitution paraphrase, low-entropy text), plus short text → inconclusive, keygen uniqueness + refusal of defaults, CLI smoke tests, MCP handshake + tools/call via subprocess.
7. **Calibration** — an empirical minimum-detectable-length experiment (`experiments/min_tokens.py`): Monte Carlo sweep over text lengths reporting TPR at fixed FPR, validated against the analytic power curve, results in `docs/min-tokens.md`.

## Honesty framing (non-negotiable)

- Detects **Kirchenbauer-style green-list watermarks only**. Does NOT detect SynthID Text (trained classifier detector, not a published key) and does not detect arbitrary AI text. README and CLI help must say this clearly.
- The z-score is a false-positive rate, not a certainty percentage (prosecutor's fallacy — see post3-skeleton.md Length ¶1 notes).
- Short/low-entropy text carries no signal (25-token/entropy caveat).

## Positioning: the open scheme, not SynthID

**This tool detects the open Kirchenbauer scheme (HF `WatermarkingConfig`), not SynthID Text.** The two schemes don't interoperate:

| | SynthID Text | Kirchenbauer green-list (this tool) |
|---|---|---|
| Generation | g-function + tournament sampling | hash-seeded green/red vocab split |
| Detection | trained classifier (deployer trains it, 10k examples min, private config) | z-test — just the key, no model |
| Detector availability | per-deployment, must be trained by the deployer | instant, anyone with the key |

**Justification (why this tool exists and isn't a SynthID rival):**

1. **Not an addition to SynthID — impossible by construction.** The z-test cannot detect SynthID-watermarked text: different math, and SynthID's detector is a trained model tied to a private config, not a published key. The tool detects the *other* scheme.
2. **The gap is real.** HF `transformers` ships both schemes: `SynthIDTextWatermarkingConfig` *and* `WatermarkingConfig` (the Kirchenbauer-style green-list scheme). A builder using HF's `WatermarkingConfig` today has no standalone detector — Kirchenbauer's repo is torch-dependent and research-grade. Barium makes green-list detection free and instant.
3. **Complement, not rival.** SynthID is a production watermarking service embedded in Google's ecosystem; barium ships no generation story (the embedder is a labelled demo). The one honest competitive wrinkle: free green-list detection makes that scheme more attractive relative to SynthID (whose detection friction — training your own classifier — is real). The README owns this rather than blurring it.
4. **Series alignment.** Post 3's mechanism section teaches the Kirchenbauer scheme (the z-score, green lists, and 25-token claims all describe it) — so the tool detects exactly what the post teaches. SynthID was always the production footnote, not the post's subject.

**Positioning rule for all prose (README, CLI help, blog):** "A detection tool for the open green-list scheme — not a SynthID tool." Never imply it detects SynthID; cite SynthID in related work as the scheme this tool deliberately does not cover, with a pointer to the HF integration for builders who need it.

## Related work to cite in the README

- **[jwkirchenbauer/lm-watermarking](https://github.com/jwkirchenbauer/lm-watermarking)** — the official research repo and reference implementation (torch-dependent, research-grade). Cite as the canonical algorithm.
- **[Kirchenbauer et al. 2023](https://arxiv.org/abs/2301.10226)**, "A Watermark for Large Language Models" (ICML) — the paper.
- **[SynthID Text](https://www.nature.com/articles/s41586-024-08025-4)** (Nature 2024) and the [HF integration](https://huggingface.co/blog/synthid-text) — the production implementation for closed deployment; cited as the scheme this tool deliberately does NOT cover (trained-classifier detection, private config). Builders who need SynthID detection use the provider's own detector.
- **[fortil/watermark-ia-detector-mcp](https://github.com/fortil/watermark-ia-detector-mcp)** — detection-only MCP for C2PA/XMP/metadata provenance + remote provider verifiers. Different layer of the same Art 50(2) problem; complementary, not competing.
- **[Sadasivan et al.](https://arxiv.org/abs/2303.11156)** — spoofing/evasion attack surface (key inference with ~1M queries), for the threat-model doc.

## EU AI Act framing

Art 50(2) requires outputs marked "in a machine-readable format and detectable as artificially generated or manipulated", with solutions "effective, interoperable, robust and reliable as far as this is technically feasible" — and names "the costs of implementation" as a proportionality factor. A one-command, zero-cost detector lowers that cost. The tool is the proof-of-work for the post 3 argument; the post is the distribution channel for the tool.

## Threat model (docs/threat-model.md)

The key is the attack surface: if it leaks or is inferable, attackers spoof (compose human text that flags as AI) or evade (paraphrase away from green tokens deliberately). Private mode (Kirchenbauer §5): key secret, detection behind a rate-limited API — but then third parties can't verify. Multiple keys as mitigation (k > 1, Bonferroni-corrected detection).

## Build plan (for the new VS Code window)

1. `pyproject.toml` — name `barium-watermarking`, console_scripts: `barium=barium.cli:main`, `barium-mcp=barium.mcp_server:main`
2. Package `barium/` — `detector.py` (GreenListDetector, DetectionResult dataclass), `embedder.py` (reference demo embedder), `keygen.py`, `cli.py`, `mcp_server.py`
3. `tests/` — confusion-matrix tests (TP round-trip, TN low-z, FP-rate Monte Carlo, FN attacks: truncation, token substitution, low-entropy), inconclusive short text, keygen, CLI, MCP subprocess; `experiments/min_tokens.py` calibration for the minimum detectable length
4. `README.md` — series link (https://leiwe.partners/insights/eu-ai-act-watermarking), z-test explainer, honesty notes, no-hosting stance, related work, MIT licence
5. `docs/threat-model.md`, `.gitignore`, `LICENSE` (MIT, Leiwe & Partners)
6. Init git, create the GitHub repo under `LeiweAndPartners`, push

## Planning documents (copied from watermark-demo)

- `docs/plans/writing-style-guide.md` — the house style (UK English, contractions, no em-dash defaults, no LLM tells, concrete evidence, honest uncertainty)
- `docs/plans/series-plan.md` — the blog series structure
- `docs/plans/post3-plan.md` — post 3 sources and claims (every number in the README must trace here)
- `docs/plans/post3-skeleton.md` — the full post 3 draft skeleton (mechanism, attacks, implementation)
- `docs/plans/bi-claude-watermark-article-notes.md` — Business Insider article notes (market context)

## Sufficient context to start the build?

Yes — this README is self-contained for the build: scope (six deliverables), the honesty framing, related work to cite, the EU AI Act framing, the threat model, and a numbered build plan. The planning docs are supporting context, not required reading for the build:

- **Required**: this README alone specifies the package layout, CLI surface, MCP tools, test matrix, and the non-negotiable honesty framing
- **Useful for the README prose**: `post3-plan.md` (the claims-check source — every number in the tool's README must trace here) and `writing-style-guide.md` (the README's prose register)
- **Background only**: `post3-skeleton.md` (the full draft — the mechanism/attack sections explain *why* the tool's caveats exist), `series-plan.md`, `bi-claude-watermark-article-notes.md`

One gap to know about: the exact Kirchenbauer algorithm details (hash construction, green-list derivation from the seed, the z-score formula) are summarised here but not specified line-by-line — the build window should work from [arXiv:2301.10226](https://arxiv.org/abs/2301.10226) §2 and the reference implementation ([jwkirchenbauer/lm-watermarking](https://github.com/jwkirchenbauer/lm-watermarking)) rather than from this brief alone.

## Post-3 draft guidance: when to name barium vs SynthID

The tool's existence changes a few draft paragraphs. The rule: **name the scheme, not just the product** — the post teaches the Kirchenbauer scheme, so barium slots in where the post discusses *that* scheme's detection; SynthID stays where the post discusses production deployment.

**Where barium belongs (Kirchenbauer-scheme detection):**

- **Mechanism ¶3 (the detector)** — the natural home. The paragraph already teaches the z-test ("anyone with the key re-derives the green lists and counts"); one clause at the end: "we've packaged this as a free, dependency-free detector ([barium](https://github.com/LeiweAndPartners/barium-watermarking))". The demo prose and the tool are the same scheme.
- **Implementation ¶1** — after "which means either self-hosted weights or an API that exposes logit biasing", barium is the detection-side companion: generation via SynthID Text or HF `WatermarkingConfig`, detection via barium for the green-list scheme. One clause, not a section.
- **Builder Bottom Line** — the actionable close: "if you use the open green-list scheme, detection is a one-command z-test (barium); if you use SynthID Text, detection is a trained classifier you deploy yourself".

**Where SynthID stays (production deployment):**

- **Implementation ¶1-¶2** — SynthID Text is the production implementation; the HF snippet stays as-is.
- **The self-hosted PII scenario** — SynthID Text in your own middleware is the generation-side answer; barium doesn't change this (it's detection-only).
- **Mechanism ¶1** — SynthID Text stays as the production footnote in the history sentence.

**Where neither belongs:** the attack surface section (attacks apply to the scheme, not to tools), and the Code Blindspot (code is unwatermarkable regardless of scheme).

**The one sentence to avoid:** anything implying barium detects SynthID output. If a draft sentence pairs the two, check the scheme: "detect AI text" → neither tool honestly does this; "detect green-list watermarks" → barium; "deploy SynthID Text" → the HF integration.
