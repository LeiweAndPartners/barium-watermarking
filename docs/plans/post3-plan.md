# Post 3 Plan: How Text Watermarking Works

**Status:** Drafting — skeleton at `post3/post3-skeleton.md` (headings + paragraph briefs; Marcus writes prose, Copilot edits)

## Audience & Goal
Technical builders. Takeaway: *text watermarks are a statistical signal in word choice — they survive copy-paste but die to paraphrase, and they need length.*

## Core Claim
The model secretly favours "green" tokens during generation; a detector that knows the key counts green vs red and computes a z-score. Short text = no signal.

## Outline
- **Executive Summary** — the mechanism; the length limit; what survives; builder guidance (SynthID in validation middleware)
- **The mechanism** — Kirchenbauer et al. 2023: green token biasing, statistical test with p-values; the demo as the centerpiece
- **The length problem** — "as few as 25 tokens" for high-entropy text (Kirchenbauer §1); 98.4% detection at z=4 in the paper's 200-token experiments; why prescriptive/factual answers are harder to watermark (Appendix G: low-entropy TriviaQA answers yield weak detection statistics)
- **The attack surface** — copy-paste survives (watermark detectable "from only a contiguous portion" of the text), paraphrase dies (but note: "a few sentences that are partially or not at all paraphrased can be sufficient to trigger detection"), translation dies, shortening dies (the demo shows all four). Translation attack is directly tested: He et al. 2024 (ACL 2024) — current watermarks "lack consistency" across languages; their Cross-lingual Watermark Removal Attack (CWRA: generate in a pivot language, then translate) drops AUC to random-guessing level. Quality caveat cuts both ways: CWRA achieved removal "without performance loss" with a good translation pipeline — so the mistranslation risk depends on translation quality (smaller/weaker translation models drift more, per Sadasivan et al.'s 222M paraphraser result). Like Bible translation: English versions differ depending on whether they trace to the Masoretic text or the Septuagint — the "same" meaning, different words, and some versions lose more in transit
- **The code blindspot** — code is "text" but practically unwatermarkable; the EU hasn't addressed it
- **Implementation: SynthID Text in your stack** — generation-time, not post-hoc: you need logits access (self-hosted weights, or an API that exposes logit biasing); HuggingFace `SynthIDTextWatermarkingConfig` as a logits processor on any open-weight model; detector for inbound-text validation middleware; what you can't do (can't watermark a closed API you don't control)
- **The compute cost** — watermarking is a logits processor: a per-token bias applied on top of the model's forward pass, so overhead is negligible relative to inference itself (no published latency numbers — state qualitatively, ⚠️ verify against the Nature paper's supplementary if drafting needs a figure). Detection is a separate pass: SynthID's trained classifier costs more than a Kirchenbauer-style z-test (which is just counting green tokens), but both are far cheaper than generation. The real cost is operational: key management, detector availability, and logging which outputs were watermarked
- **Security: the key is the attack surface** — if the watermark key leaks or is inferable, attackers can spoof (Sadasivan et al.: ~1M queries to a watermarked model sufficed to infer green lists and compose human text that flags as watermarked). Private mode (Kirchenbauer §5): keep the key secret, run detection behind a rate-limited API — but then third parties can't verify, which cuts against transparency duties
- **The self-hosted PII scenario** — high-risk AI system, open weights, confidential/PII data that can't leave your perimeter: you can't use a hosted watermarking API, so in-content watermarking via SynthID Text in your own middleware is the only option that satisfies both data residency and Art 50(2). Metadata alone (C2PA-style) is trivially strippable — copy-paste loses it — which is post 1's two-layers point; in-content survives. Interpretation flag: whether metadata-only marking satisfies Art 50(2) is unresolved; in-content is the defensible reading. Key nuance: Art 50(2)'s assistive-editing exemption means pass-through/light-edit middleware is out of scope — the duty bites when your middleware *generates* content; and Art 50(2) names cost-of-implementation as a proportionality factor, so "we can't watermark at any price" is a defence the Act itself provides
- **Builder bottom line** — SynthID Text in validation middleware; don't strip watermarks when manipulating output (ToS + Art 99(4)(g))

## Claims to Verify
- ✅ Verified: Kirchenbauer mechanism (green tokens, statistical test, ICML 2023) — arXiv
- ✅ Verified: length threshold — paper claims "as few as 25 tokens" (high-entropy text); hard red-list variant detectable at 16 tokens; 98.4% empirical detection at z=4; low-entropy text needs more
- ✅ Verified: SynthID Text open-source status (Apache 2.0, Nature paper, reference + production HuggingFace impl)
- ✅ Verified: "Anthropic hasn't released detection means yet" — support article says detection is "forthcoming"
- ✅ Verified: Art 50(2) text marking; Art 50(4) public-interest text disclosure; human editorial control exemption
- ✅ Verified: translation attack — He et al. 2024, "Can Watermarks Survive Translation?" (ACL 2024, arXiv:2402.14007): introduces cross-lingual consistency; CWRA (pivot-language generation + translation) drops watermark AUC to random-guessing level "without performance loss"; proposes X-SIR defense. Paraphrase attack — Sadasivan et al. 2023 (arXiv:2303.11156, TMLR): recursive paraphrasing drops watermark TPR@1%FPR from 99.3% to 9.7% on 300-token passages; smaller 222M paraphraser degrades quality more than 11B. Frame the mistranslation point as quality-dependent, not absolute
- ⚠️ VERIFY: OpenAI watermarking plans — openai.com blocks fetching (403); background: text watermark built then shelved (2024 reporting) over circumvention/user-impact concerns; Aaronson's cryptographic scheme was their research line (cited in Kirchenbauer §8). Re-verify before drafting
- ✅ Verified: Anthropic's latest announcement (Oct 2, 2026, Claude Frontier Academy) — nothing watermarking-related in the newsroom; watermark position remains the support article ("forthcoming")
- ✅ Verified: open-weight models ship unwatermarked — watermarking requires logits control at generation time; SynthID Text (Apache 2.0) exists so self-hosters can apply it themselves. Interpretation flag: self-hosting open weights may make *you* the Art 50(2) provider
- ✅ Verified: DeepSeek & Qwen APIs — no watermarking mentioned in DeepSeek API docs or Qwen blog/announcements (Qwen3Guard is a safety classifier, not a watermark). No public evidence of watermarking in either
- ✅ Verified: HuggingFace API — `watermarking_config` parameter on `generate()` accepts `SynthIDTextWatermarkingConfig` (logits processor, "small bias to randomly selected set of 'green' tokens") — confirmed in transformers GenerationConfig docs
- ⚠️ VERIFY: SynthID Text compute overhead — no published latency/throughput numbers in HF docs; check Nature paper supplementary for overhead figures before quoting any

## Sources

### Papers
- **Kirchenbauer et al. 2023, "A Watermark for Large Language Models"** (ICML 2023) — [arXiv:2301.10226](https://arxiv.org/abs/2301.10226) · [HTML v4](https://arxiv.org/html/2301.10226v4)
  - Mechanism: hash of the previous token seeds a PRNG that partitions the vocabulary into green/red lists; green-list logits boosted by δ ("soft" rule, Algorithm 2)
  - Detection: one-proportion z-test, z = (|s|G − γT)/√(Tγ(1−γ)); reject at z > 4 → false-positive rate 3×10⁻⁵
  - Length: "detectable from short spans of tokens (as few as 25 tokens)"; hard-list variant at 16 tokens; 98.4% empirical detection at z=4
  - Removal: "requires modifying roughly one quarter of the tokens or more"
  - Attacks (§7): paraphrasing (manual + automated T5 span attack), generative/emoji attacks (Goodside), homoglyph & zero-width attacks, tokenization attacks
  - Code blindspot: the paper's own low-entropy example is code — `for(i= 0;i<n;i++) sum+=array[i]`
  - Factuality (Appendix G): low-entropy factual answers yield weak detection stats, <4-point Exact Match drop — factual Q&A is a worst case for watermarking
  - Public vs private mode (§5): detector can be open-sourced without model access — the SynthID Text pattern
- **Fang, Jaggi & Argyraki 2017, "Generating Steganographic Text with LSTMs"** (ACL 2017 Student Research Workshop) — [ACL Anthology](https://aclanthology.org/P17-3017/): LSTM-based stegosystem for covert messaging (privacy motivation); high-quality stego text, improved capacity
- **Ziegler, Deng & Rush 2019, "Neural Linguistic Steganography"** (EMNLP-IJCNLP 2019) — [ACL Anthology](https://aclanthology.org/D19-1115/): arithmetic coding with neural LMs; encodes secret messages, receiver decodes bits — no hypothesis test (the z-test is Kirchenbauer's contribution)
- **Dathathri et al. 2024, "Scalable watermarking for identifying large language model outputs"** (SynthID Text) — [Nature](https://www.nature.com/articles/s41586-024-08025-4) (paywalled; verified in earlier session)
- **Sadasivan et al. 2023, "Can AI-Generated Text be Reliably Detected?"** (TMLR) — [arXiv:2303.11156](https://arxiv.org/abs/2303.11156) · [HTML v4](https://arxiv.org/html/2303.11156v4)
  - Recursive paraphrasing attack: watermark TPR@1%FPR 99.3% → 9.7% on 300-token passages; 2 rounds sufficient to drop below 50%
  - Quality trade-off: 77% of paraphrases rated high-quality content preservation, 89% grammar (MTurk study); QA benchmark accuracy unchanged — meaning mostly survives
  - Smaller paraphraser = worse quality: 222M T5 degraded perplexity more than 11B DIPPER / 7B LLaMA-2 — supports the "translation with small models risks mistranslation" point
  - Spoofing: attacker can infer green lists by querying a watermarked model ~1M times, then compose human text that flags as watermarked (AUROC 99.8% → 1.3%)
  - Theory: best-possible detector AUROC is bounded by the TV distance between human and AI text distributions — detection gets harder as models improve
- **He et al. 2024, "Can Watermarks Survive Translation? On the Cross-lingual Consistency of Text Watermark for LLMs"** (ACL 2024) — [arXiv:2402.14007](https://arxiv.org/abs/2402.14007) · [code: X-SIR](https://github.com/zwhe99/X-SIR)
  - The direct translation-attack citation: current watermarks "lack consistency" when text is translated (2 LLMs × 3 watermarking methods)
  - CWRA (Cross-lingual Watermark Removal Attack): generate in a pivot language, translate to target — AUC drops to random-guessing level, "without performance loss"
  - Nuance for the post: "without performance loss" means a good translation pipeline removes the watermark at near-zero quality cost — the mistranslation risk argument holds for weaker translation models, not strong ones
  - X-SIR: their defense — invariant watermark across languages (research-stage)

### Provider sources
- **DeepMind SynthID** — [deepmind.google/technologies/synthid](https://deepmind.google/technologies/synthid/): embedded across Google's generative products; SynthID Detector verification portal (early testers: journalists); Gemini checks image/video/audio for SynthID
- **SynthID Text repo** — [github.com/google-deepmind/synthid](https://github.com/google-deepmind/synthid) (Apache 2.0; reference + production HuggingFace implementations) — verified previously
- **HuggingFace transformers docs** — [GenerationConfig](https://huggingface.co/docs/transformers/main/en/main_classes/text_generation): `watermarking_config` parameter accepts `SynthIDTextWatermarkingConfig`; watermarking implemented as a logits processor on `generate()`
- **Anthropic** — [support article](https://support.anthropic.com/en/articles/11105898-guidelines-for-identifying-ai-generated-content) (redirects to support.claude.com): detection means "forthcoming"; [newsroom](https://www.anthropic.com/news) checked Oct 2026 — no watermarking announcements
- **DeepSeek** — [API docs](https://api-docs.deepseek.com/): OpenAI/Anthropic-compatible API; no watermarking mention anywhere in docs
- **Qwen** — [research blog](https://qwen.ai/research): no watermarking releases; Qwen3Guard (Sep 2025) is a prompt/response safety classifier, not a watermark

### Legal
- [Art. 50(2)](https://artificialintelligenceact.eu/article/50/) — text-marking duty. Specifics in the text:
  - Applies to "providers of AI systems, **including general-purpose AI systems**" — middleware builders generating synthetic text are providers, no need to be the model developer
  - Outputs must be "marked in a **machine-readable format** and detectable as artificially generated or manipulated"
  - Proportionality named in the text: "effective, interoperable, robust and reliable **as far as this is technically feasible**", weighing "the specificities and limitations of various types of content, **the costs of implementation** and the generally acknowledged state of the art, as may be reflected in relevant technical standards" — cost is an explicit defence
  - **Assistive-editing exemption**: duty does not apply "to the extent the AI systems perform an assistive function for standard editing or do not substantially alter the input data provided by the deployer or the semantics thereof" — pass-through/light-edit middleware is out of scope; content-generating middleware is in
  - In force **2 August 2026** (per Art 113) — already in force; the series' "2 December 2026" date is the GPAI enforcement date
- [Art. 50(4)](https://artificialintelligenceact.eu/article/50/) — deployer disclosure for text "published with the purpose of informing the public on matters of public interest"; exempt where content "has undergone a process of **human review or editorial control**" with a person holding editorial responsibility
- [Art. 50(7)](https://artificialintelligenceact.eu/article/50/) — Commission codes of practice on marking; may adopt an implementing act with common rules if codes prove inadequate (standards still moving)
- [Art. 25(4)](https://artificialintelligenceact.eu/article/25/) — value chain: high-risk providers and third-party component suppliers must agree in writing on info/technical access — **open-source carve-out**: does not apply to components under a free and open-source licence (other than GPAI models). Apache-2.0 SynthID Text = no written-agreement obligation toward DeepMind; integrator's own obligations remain
- [Art. 25(1)(b)](https://artificialintelligenceact.eu/article/25/) — "substantial modification" of a high-risk system makes the modifier the provider
- [Art. 99(4)(g)](https://artificialintelligenceact.eu/article/99/) — penalties for Art 50 breaches (€15M / 3%)

### Gaps
- **SynthID Text token minimum**: SynthID's docs don't publish a token threshold — attribute the 25-token figure to Kirchenbauer, not SynthID
- **SynthID Text compute overhead**: no published latency numbers in HF docs — if the post quotes overhead, verify against the Nature paper supplementary first; otherwise keep it qualitative ("negligible relative to inference")
- **OpenAI status**: site unfetchable (403) — verify watermarking plans via secondary reporting before drafting; do not state OpenAI's current position without a source
- **Chinese providers**: no public evidence of watermarking (DeepSeek, Qwen) — frame as a compliance gap for EU-market deployments rather than an accusation; Art 50(2) applies to providers placing systems on the EU market regardless of origin

## Visuals
- Watermark demo (as-is). No new build.

## Cross-Links
- Post 1 (layers), post 2 (image), post 4 (audio), main guide

## Style Notes
- The demo does the explaining — write prose around it. "Imagine the model has a secret coin flip for every word."
- Translation-attack analogy: Bible versions differ depending on whether they trace to the Masoretic text or the Septuagint — same "source", different words, and some renderings lose more in transit. Use for the attacker's quality risk, not as a legal point. Scope to the OT ("different textual traditions", not "mistranslation" — the LXX likely reflects different Hebrew originals)
