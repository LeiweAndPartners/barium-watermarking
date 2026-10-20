# Series Plan: Digital Watermarking (4 posts)

*Follow-up series to [The EU AI Act: Global Impact & Compliance Guide](https://leiwe.partners/insights/eu-ai-act-global-impact-compliance-guide)*

## The Through-Line

**Watermarking is now law, and the grace period ends 2 December 2026. Most of the debate has been about dodging watermarks — the real question is what you need to *build*.**

Every post ends with the same builder bottom line: *build it now, open-source tools exist (SynthID), and December is closer than it looks.* Each post cross-links to the others and to the main compliance guide.

## The Four Posts

| # | Post | Audience | Core claim | Visual |
| :-- | :-- | :-- | :-- | :-- |
| 1 | **What Watermarking Covers** | Non-technical (LinkedIn, blog readers) | Two layers exist — in-content and container metadata — and only one survives contact with the real world. You're probably exempt, but platforms will down-rank AI slop anyway. | **Attack matrix** (full, as-is) |
| 2 | **How Image Watermarking Works** | Technical (builders, ML engineers) | Two families: post-hoc embedding (SynthID) and decoder-rooted (Stable Signature). Robustness is a false-positive trade-off. | **Attack matrix** (image rows only) + new image demo |
| 3 | **How Text Watermarking Works** | Technical (builders, ML engineers) | Green/red token biasing + statistical detection. Survives copy-paste, dies to paraphrase, needs ~25–50+ tokens. | **Watermark demo** (as-is) |
| 4 | **How Audio Watermarking Works** | Technical (builders, ML engineers) | The oldest domain: spread-spectrum, echo hiding, phase coding. Decades of real-world deployment (Cinavia, DCP traitor tracing). | New audio demo (listen + attack) |

## Visual Assignment

| Visual | File | Used in | Status |
| :-- | :-- | :-- | :-- |
| Attack matrix | `attack-matrix.html` | Post 1 (full), Post 2 (image rows) | Exists — needs row-splitting for post 2, + "AI watermark remover" row |
| Text demo | `watermark-demo.html` | Post 3 | Exists — as-is |
| Image demo | *new* | Post 2 | **To build** — visualise SynthID vs Stable Signature robustness |
| Audio demo | *new* | Post 4 | **To build** — embed audio clips, attack buttons (MP3, re-record) |

## Citation Conventions (shared across all posts)

1. **Legal claims** → link the exact clause on `artificialintelligenceact.eu`, e.g. `[Art. 50(2)](https://artificialintelligenceact.eu/article/50/)`. Never cite an article without the paragraph.
2. **Recitals** → link `artificialintelligenceact.eu/recital/NNN/` (e.g. Recital 133, 134) when they clarify intent.
3. **Papers** → link arXiv abstract pages (e.g. Kirchenbauer et al. 2023: `https://arxiv.org/abs/2301.10226`).
4. **Provider claims** → link the provider's own page (DeepMind SynthID, Meta Stable Signature blog, Anthropic support article).
5. **Interpretation vs. law** → always flag. "Matters of public interest" is undefined in the Act; anything beyond the black-letter text is labelled as interpretation.
6. **Unverifiable claims** → mark with ⚠️ VERIFY in the plan; resolve before drafting that post.
7. **Penalties** → cite [Art. 99(4)(g)](https://artificialintelligenceact.eu/article/99/) for Article 50 violations (€15M/3%), [Art. 99(6)](https://artificialintelligenceact.eu/article/99/) for the SME cap.

## Style Notes (from the main guide)

- Lead with stakes, not history. Scenario first, law second.
- Bold the take-home in each bullet. Tables over prose for comparisons.
- "I read it so you don't have to" energy: explain the legalese, don't quote it.
- Flag uncertainty honestly ("probably", "arguably") — but move caveats to footnotes where possible.
- End every post with the builder bottom line + cross-links.

## Open Questions (resolve before drafting)

1. **Video**: fold into post 2 as "What about video?" section (recommended) vs. standalone post 5. *Decision: fold in — video = image frames + audio track; standalone would be thin.*
2. **Audio demo feasibility**: can we generate/embed audio clips in a static HTML file? *Decision: yes — base64-encoded WAV clips, Web Audio API for attacks.*
3. **Post 1 length**: keep it short (5-min read) vs. medium (10-min). *Decision: short — it's the non-technical entry point.*
4. **Series title**: "Digital Watermarking: What it is and how it works" (original) vs. per-post titles. *Decision: keep original as series umbrella, per-post titles below.*

## Drafting Order

1. Post 1 (non-technical, highest stakes — must work for general audience) ✅ drafted
2. Post 3 (text — demo already exists, easiest technical post)
3. Post 2 (image — needs new demo)
4. Post 4 (audio — needs new demo, most research)

*Each post drafted only after its per-post plan is approved.*
