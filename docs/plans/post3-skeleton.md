# Post 3 Draft Skeleton: How Text Watermarking Works

*Working skeleton — headings and paragraph briefs only. Marcus writes the prose; Copilot edits. Metaphor slots are flagged, not filled (per style guide: metaphors are authored by the writer).*

**SEO/GEO notes for the whole post:**
- Question-based H2/H3s (matches post 1 pattern; AI search engines quote direct answers)
- Each H2 should open with a one-sentence direct answer before the nuance — GEO extracts the first sentence
- Numbers in prose (25 tokens, 98.4%, 99.3%→9.7%, €15M/3%) — specific figures get quoted by AI search
- Target length: medium (10-min read) — this is the technical deep dive, unlike post 1's short format
- UK English, contractions, no em-dash defaults, no "Bold lead-in:" rhythm (style guide)
- On "green list" clarity in the GEO sentence: the first sentence defines it implicitly ("biasing word choices toward a secret 'green list' of tokens") and para 2 explains the mechanism fully — the term doesn't need to be self-explanatory in sentence one, it needs the *mechanism* to be. GEO extracts the sentence for "how does text watermarking work", and that sentence answers it (bias word choices → count → z-score). "Green list" is the label, not the payload. If still worried, the exec summary bullet already says "the model secretly favours 'green' tokens" — the reader meets the term twice before the mechanism section

---

## Title options (pick one)

1. **How Text Watermarking Works (and Why Paraphrase Defeats It)** — matches post 1's "(and What It Doesn't)" pattern
2. **Green Tokens: How Text Watermarking Actually Works** — mechanism-forward, distinctive
3. **How Text Watermarking Works** — plain, series-consistent

*My take: option 1 — the parenthetical is the series signature and the paraphrase angle is the hook.*
> Let's go option 1 for now

---

## Executive Summary
This is a technical blog post on textual watermarking. If you're new to watermarking in general the [Watermarking Rule Explained](https://leiwe.partners/insights/eu-ai-act-watermarking) post covers when you're in or out; this one is the how for text.
*5 bullets, bold lead-ins (post 1 pattern — exempt from the "bold lead-in" tell because it's the established series format). Each bullet = one section's takeaway.*

- **The mechanism in one sentence:** the model secretly favours "green" tokens; a detector that knows the key counts green vs red and computes a z-score.
- **Length is the limit:** detectable from as few as 25 tokens (high-entropy text); short text = no signal.
- **What survives / what dies:** copy-paste survives; paraphrase and translation kill it.
- **Code is the blindspot:** code could be seen as "text" under the Act but practically unwatermarkable.
- **If you're a builder:** SynthID Text in your middleware, generation-time, and the self-hosted PII scenario makes it your only option.

*Exec summary note (resolved):* the code bullet keeps its own slot — it's the one surprise in the summary (the Act still applies to code, but nothing can satisfy it), the honest-limits anchor, and the most actionable caveat for the builder audience. The amended wording ("could be seen as") has the right hedge, consistent with Code ¶1's register. The fold-into-builder option was considered and rejected: the surprise is the point, and the 5-bullets-5-sections mapping holds.

## Introduction
---
### Intro ¶1
#### Notes
##### Para 1 — the hook (technical audience). 

*Options:*
1. **The self-hosting fork (recommended).** You're wiring an LLM into your product. Call a closed API and the provider marks the output for you. Self-host open weights — Llama, Qwen, Mistral — and nothing marks anything, and since 2 August 2026 that's your problem, not the model author's ([Art. 50(2)](https://artificialintelligenceact.eu/article/50/) makes you the provider). Before you can solve it, you need to know what a text watermark actually is. *Sets up the whole post: mechanism → attacks → implementation, and the PII scenario later pays this off.*
2. **The invisible diff.** Run the same prompt twice, diff the completions: nothing visible. No metadata, no hidden characters, no label. The mark is in the *sampling distribution*, not the text — which is why `strings` and grep find nothing and why stripping tools keep failing. *Immediately conveys the core insight (statistical signal in word choice); pairs well with the demo.*
3. **The middleware moment.** You're building validation middleware for AI outputs and someone asks "can we detect AI text inbound?" — the answer is a statistical test, not a regex, and it only works if the generator cooperated. *Most directly aimed at the builder bottom line, but starts mid-post rather than at the start.*

*My take: option 1 — it's the reader's actual decision moment (self-host vs API), it creates the obligation that makes the rest of the post matter, and it's the setup the PII scenario pays off. Option 2 is the better *opening line* if you want to lead with the mechanism's strangeness; the two can combine: open with the diff, land on the fork.*
> Agree lets go with Option 1.

##### Bullet of points to cover
- You're tasked with wiring in an automated financial report generator. All the data is private, but is based in the EU. The Product Owner has told you that the product needs to include watermarking in order to be compliant with the EU AI Act. You ask them how, they shrug and point to the legislation that says "make reasonable efforts". How do you build something with those vague specifications?
- The private-data detail is the fork: data can't leave your perimeter, so a hosted watermarking API is out, so you self-host open weights, and Art 50(2) makes *you* the provider. State this explicitly in the hook, don't leave it implied
- In this blog, we'll go through how we can watermark text, how the large AI model companies do or don't do it, then ultimately how to wire watermarking into your own stack
- NB if you want to check out when you need watermark see our [high-level watermarking post](https://leiwe.partners/insights/eu-ai-act-watermarking) — now live ("The EU AI Act: Watermarking Rule Explained", published 4 Oct 2026, 14-min read). It covers the provider/deployer split, deepfake definition, public-interest test, and the provider matrix — so post 3's intro should NOT re-explain those; link and move on
- Series link (para 3): the high-level post IS the live series entry point (post 1's content is folded into it) — link it here as the "what" companion, and don't duplicate the NB link with different anchor text. White paper goes in the footer cross-links only
- When drafting: the PO's "make reasonable efforts" is their paraphrase — the implementation section quotes the real text ("effective, interoperable, robust and reliable as far as this is technically feasible") to show the Act is more specific than the shrug suggests. Hook poses the vagueness; implementation resolves it

#### Paragraph draft
You're tasked with wiring in an automated financial report generator. All the data is private, but is based in the EU. The Product Owner has told you that the product needs to include watermarking in order to be compliant with the EU AI Act. You ask them how, they shrug and point to the legislation that says "make reasonable efforts". *How do you build something with those vague specifications?*

You know the data can't leave the perimeter so you can't outsource to a watermarking API, the LLM is a fine-tuned open-weight model, and [Article 50(2)](https://artificialintelligenceact.eu/article/50/) makes **you** the provider. So, in this blog we will cover: how current watermarking works, what survives and what dies, how the current providers do it, and how to ultimately wire watermarking into your own stack.

*Para 2 dropped — it front-ran the mechanism (green list, z-score) and para 1 is sufficient for a technical audience. The GEO direct answer now lives as the opening sentence of the Mechanism section. History/key-paper content moved there too.*

## The Mechanism: Green Tokens and a Statistical Test

### Mechanism ¶1
#### Notes
##### Para 1 — direct answer (GEO slot) + history.

"Text watermarking works by biasing the model's word choices toward a secret 'green list' of tokens; detection is a statistical test that counts green tokens and computes a z-score." Then one sentence of grounding: the idea dates to Kirchenbauer et al. 2023 (ICML, University of Maryland) — "A Watermark for Large Language Models" — with Google's SynthID Text following in Nature (2024). *This opening sentence is the GEO extraction target for "how does text watermarking work".*

##### Bullet of points to cover
- Background: when did people first start to work on it? (Kirchenbauer et al. 2023, ICML; SynthID Text in Nature 2024)
- Lead into the key paper (Kirchenbauer?)
- Key aspect is a z-score. Resolved: it's a one-proportion z-test, not a t-test — the expected proportion is known (half the vocabulary, γ=0.5) and the sample is long enough for the Gaussian approximation, so no t-distribution correction. The z-score measures how many standard deviations the observed green count sits from the fair-coin expectation (T/2). z > 4 → false-positive rate 3×10⁻⁵ (3 in 100,000)
- Z-test attribution (resolved): **Kirchenbauer introduced the one-proportion z-test for watermark detection** — it's their §2 contribution, not Fang/Ziegler's. Fang 2017 and Ziegler 2019 were steganography (encoding hidden *messages*): the receiver decodes bits, there's no hypothesis test at all. AWT (Abdelnabi & Fritz 2021) used learned decoders, again no z-test. The z-test is what makes Kirchenbauer's scheme *detection* rather than *decoding* — and it's why the detector needs no model access
- History before Kirchenbauer (one sentence max): rule-based linguistic watermarking goes back to the early 2000s (Atallah et al. 2001, synonym/parse-tree edits) but degraded quality; neural steganography (Fang 2017, Ziegler 2019) hid messages, not provenance; AWT (Abdelnabi & Fritz, IEEE S&P 2021) was the first learned end-to-end scheme; Aaronson/OpenAI announced a cryptographic scheme Nov 2022, ~2 months before Kirchenbauer's submission. Kirchenbauer was the first *practical* scheme: no retraining, open-source detector, statistical test with interpretable p-values
- Why pre-LLM work existed (motivation, not GPT-1): the 2000s rule-based schemes were for *document provenance and tamper-proofing* — proving a document's origin/integrity, tracing leaks, copyright protection of digital text. Targets were classical NLP systems, rule-based MT, and structured prediction (Venugopal 2011 watermarked statistical MT output). Not GPT-1 — GPT-1 is 2018; the 2000s work predates it entirely. The neural-era work (Fang 2017, Ziegler 2019) targeted LSTMs and small LMs for *steganography* (covert messaging), and the modern motivation (detecting machine-generated text at scale, misuse prevention) only arrived with ChatGPT-era LLMs — which is exactly why Kirchenbauer's Jan 2023 paper landed when it did
- Canary trap connection (verified via Wikipedia): yes, similar — and the lineage is real. Clancy *coined* the term in Patriot Games (1987) but did NOT invent the technique: MI5 and other agencies used it for years as the "barium meal test" (per Peter Wright's Spycatcher, also 1987). Clancy's Jack Ryan describes exactly the synonym-shuffle method: "a thesaurus program to shuffle through synonyms, and you make every copy of the document totally unique" — each copy uniquely identifiable, so a verbatim quote identifies the leaker. That's document fingerprinting: per-copy unique variants trace the leak. Text watermarking differs: one shared statistical signal across ALL outputs from a model, detecting the *source class* (AI vs human), not a specific copy. Confirmed real-world uses: Star Trek III script leak (Roddenberry), Tesla 2008, NBA 2014, Wagatha Christie 2019, Apple 2023. Kirchenbauer's paper even cites the zero-width-space fingerprinting technique (Zach Aysan) in its related work — the family tree is direct
- TRL framing (interpretation, flag as mine): at publication Kirchenbauer was ~TRL 3-4 (proof of concept on OPT models); the technique family is now TRL 9 via SynthID Text (production, open-sourced). Nice builder-friendly maturity marker for an EU audience — but it's our framing, not the papers'

#### Paragraph draft
Text watermarking works by biasing the model's word choices toward a secret "green list" of tokens; detection is a statistical test that counts green tokens and computes a [z-score](https://en.wikipedia.org/wiki/Z-test). But its roots are far older: textual fingerprinting, where signals are hidden in word choices so the source can be identified later. Intelligence agencies ran a per-copy version known as the [barium meal test](https://en.wikipedia.org/wiki/Canary_trap) or canary trap (coined by Tom Clancy in his 1987 novel Patriot Games) to trace leaks. Synonyms were shuffled uniquely into every copy of a document, meaning that when news leaked to the press, agencies could identify the source by the exact words used. Academic versions followed for document provenance and copyright protection. And by 2017 neural network approaches using LSTMs and small language models were used for covert messaging ([Fang et al. 2017](https://aclanthology.org/P17-3017/), [Ziegler et al. 2019](https://aclanthology.org/D19-1115/)). What changed with LLMs was the scale: as machine-generated text began to flood the web, identifying the source became a serious detection problem. The mechanism comes next, but briefly: [Kirchenbauer et al.](https://arxiv.org/abs/2301.10226) published the first practical LLM watermark at ICML in 2023, and Google's [SynthID Text](https://www.nature.com/articles/s41586-024-08025-4) was the production implementation that followed in Nature in 2024, now open source.

### Mechanism ¶2
#### Notes
##### Para 2 — the coin flip idea.

"Imagine the model has a secret coin flip for every word" (from the plan's style notes — but the final metaphor is yours to author). Before each token, a hash of the previous word seeds a random split of the vocabulary into green and red; green-list logits get a boost.

##### Bullet of points to cover
- Metaphor slot: the coin flip is yours to author (style guide: metaphors are authored by the writer)
    - Essentially uses a z-score to measure the differences between a fair coin, and a weighted one (watermark)

#### Paragraph draft
So why is watermarking necessary? Usually the simplest way of marking text is to add metadata to the file. However, this is trivially easy to bypass: you can simply copy-paste the data into a new file, or go in and edit the metadata, but embedded watermarks remain. That is what enables the detection of copyright infringements, academic fraud, and other malicious uses of AI-generated text. But how does text watermarking actually work with LLMs? Kirchenbauer adapted the earlier fingerprinting techniques to consistently hide a single fingerprint inside all of a model's outputs. At generation time, a hash of the previous token seeds a pseudo-random split of the vocabulary into a "green list" and a "red list", and a logits processor adds a small bias to the green-list tokens before the model samples. No weights are touched: the bias is applied to the logits the final layer produces, not to the model itself. The result is that the output becomes more prone to select green-list tokens over others. This is similar to a biassed coin: if you weight the coin heavily the fingerprint becomes rather obvious, but if you make the bias weaker it still may be detectable, just only statistically and not to the human eye.

#### Visual Demo
Plan: Animated sorting of how the logits are labelling green and red. NB We need to be very careful between the definition of tokens and words.

### Mechanism ¶3
#### Notes
##### Para 3 — the detector.

No model access needed: anyone with the key re-derives the green lists and counts. One-proportion z-test; reject at z > 4 → false-positive rate 3×10⁻⁵. *This is the "providers mark, deployers disclose" moment for text: the mark is statistical, the disclosure is human-readable.*

##### Bullet of points to cover
- No model access needed — anyone with the key re-derives the green lists and counts
- One-proportion z-test; reject at z > 4 → false-positive rate 3×10⁻⁵
- "Providers mark, deployers disclose" moment for text: the mark is statistical, the disclosure is human-readable
- California SB 942 (verified against the bill text): covered providers (GenAI systems with 1M+ monthly users, publicly accessible in California) must offer an AI detection tool "at no cost to the user" that is "publicly accessible" (§22757.2(a)(4)), with reasonable security limitations allowed, and must support an API (§22757.2(a)(6)). NB: the tool must detect image/video/audio — text is NOT in the detection-tool scope (§22757.2(a)(1)); text only appears in the latent-disclosure duty (§22757.3(b)). So the "public key" argument holds for the tool mandate, but SB 942's detection scope is media, not text — flag this honestly
- Tension worth one sentence: a public key lets anyone verify (transparency) and lets attackers spoof (Sadasivan et al. inferred green lists with ~1M queries). SB 942's "reasonable limitations on access" carve-out (§22757.2(a)(4)(B)) is the legislature's answer to exactly this

#### Paragraph draft
Once we have generated the watermark, the next step is to detect it. To do this we need to know what the green/red list is. This list is created by a seeded hash of the previous token, meaning that anyone who has the hash function can re-derive the green list for any position and then count the frequency of "green list" tokens. No LLM is loaded, LLM weights are unaffected; the detector just counts and assesses whether the frequency of green tokens is significantly higher than the null expectation. This is done by calculating the z-score: the null hypothesis is rejected when z > 4, where the p-value is ~0.00003. This satisfies the EU AI Act's machine-readable requirement, however you will still need to disclose in a human-readable manner too. Additionally, this low-cost technique is a sustainable answer to California's SB 942, where covered providers (GenAI systems with over 1 million monthly users, publicly accessible in California) must offer a "publicly accessible" AI detection tool "at no cost to the user", available via an API (though note the tool mandate covers image, video and audio; text sits in SB 942's latent-disclosure duty). However, while publicly accessible detectors are great for transparency, the risk is that attackers can infer the green lists by querying a watermarked model repeatedly (~1 million queries, roughly $50) and so spoof your system outputs (essentially forging your watermark).

#### Visual Demo
Plan: Animation to show how the detector works, must include the hash, etc. Show the z-score distributions etc.

### Mechanism ¶4
#### Notes
##### Para 4 — section conclusion: the trade-off, and where it breaks.

*Reframed per Marcus: points 1-2 (metadata advantages) folded into para 2; point 3 (competitors) dropped to the revisit list. This paragraph is now purely the conclusion: the design trade-off and the hand-off to the next two sections.*

*Link fix (3 → 4):* para 3 ends on the spoofing risk ("attackers can infer the green lists... and spoof your outputs"). This paragraph should pick that thread up. Suggested bridge: "That spoofing risk is the first crack in an otherwise elegant design — and it's not the only one."

##### Bullet of points to cover
- The design trade-off in one line: the bias is a dial (δ) — heavier bias = stronger signal but more quality risk; lighter = invisible but weaker stats. This is the robustness/quality trade-off that the Length Problem section picks up
- Hand-off: the mechanism is sound, but it has two known limits — length (next section) and attacks (the section after). Don't oversell here; the honest limits live in the Builder Bottom Line

#### Paragraph draft
Overall, Kirchenbauer's technique produces a reasonable trade-off: create a subtle bias towards a secret list of tokens at generation, then assess the distribution of these tokens at detection. It doesn't drastically affect outputs, runs at low compute levels, and is robust enough to discourage the majority of users from removing the watermark (removal requires modifying roughly a quarter of the tokens). No system is perfect, though, and text-embedded watermarks do have vulnerabilities (for more, see the next section). The technique is adaptable: to be more secure, one adjusts the bias of the green list and regularly rotates hash keys. The result is an arms race between the embedders and the strippers, and the next two sections cover where the current battles are: length (the signal needs room) and attacks (what survives and what dies).

*Proofing notes (remaining fixes):*
1. **Duplication resolved** — the paragraph had two versions of the conclusion merged (the Option A attempt + the old draft). The merged version above keeps your Option A opening (mechanism as the subject of the trade-off sentence) and drops the duplicated second "Overall, Kirchenbauer's technique..." sentence
2. **"create a subtle bias"** → grammar: the sentence needs "creating" or a colon structure — "produces a reasonable trade-off: creating a subtle bias... and then assessing..." (parallel gerunds)
3. **"enouguh"** → "enough" (typo)
4. **"doesn't drastically affect outputs"** — defensible (Appendix G: <4-point Exact Match drop), keep
5. **"robust enough to discourage the majority of users"** — evidence anchor added: removal requires modifying ~a quarter of tokens (Kirchenbauer §2)
6. **"However, it is worth remembering no system is perfect"** — style-guide LLM tell; trimmed to "No system is perfect, though" and moved after the strengths so the paragraph ends on the hand-off, not the caveat
7. **Key rotation** — kept but it's deployment practice, not Kirchenbauer's technique (feeds the Security section)
8. **"arms race"** — kept as the closing image, attributed to the attack surface section via "the next two sections cover where the current battles are"


*Demo slot:* the watermark demo goes here — "the demo does the explaining, write prose around it."

#### Demo placement (thoughts)
*Current plan: demo after the Mechanism section's conclusion. Two options:*

1. **After para 2 (mechanism), before para 3 (detector) — recommended.** The demo shows generation-time biasing (green/red labelling of logits), which is para 2's content. A reader who has just seen the mechanism can *watch* it; then para 3's detector animation follows as its own beat. Two demos, two beats, each right after the paragraph it illustrates. This also fixes a flow problem: para 3's prose already describes the detector animation ("show the hash, the z-score distributions"), so the detector demo belongs after para 3, and the generation demo after para 2.
2. **Both demos at the end of the section** — keeps the prose uninterrupted, but the reader meets two animations back-to-back after the conclusion, and each demo is then far from the paragraph that explains it.

*My take: split them — generation demo after para 2, detector demo after para 3. Each demo illustrates the paragraph it follows, and the section reads prose → watch → prose → watch. The conclusion (Mechanism para 4) then lands after both demos, which is where a section conclusion belongs.*

*Adjustments needed either way:*
- The generation demo needs the tokens-vs-words care your NB flags (green list is tokens, not words)
- The detector demo should show the hash → re-derive → count → z-score chain, and the z-score distribution with the threshold at z=4
- If the demo currently bundles generation + detection in one widget, consider splitting it into two beats to match the new placement

## The Length Problem: 25 Tokens, Give or Take

### Length ¶1
#### Notes
##### Para 1 — bridge from the mechanism section, then the direct answer (GEO slot).

*Flow fix per Marcus: this is the first paragraph after the Mechanism section's conclusion, which ended on the arms race hand-off ("length (the signal needs room) and attacks (what survives and what dies)"). Length ¶1 should pick that thread up, not jump cold into the direct answer. Suggested bridge: "The first limit is length." Then the direct answer lands as the second sentence — the GEO extraction still works because the answer sentence is intact and near the top of the section.*

Direct answer (keep intact for GEO): "Text watermarks need roughly 25 tokens of high-entropy text to detect reliably; short answers carry no signal." Hard red-list variant detects at 16; the paper's soft watermark hit 98.4% detection at z=4 on 200-token generations.

##### Bullet of points to cover
- Bridge from the mechanism conclusion: "the first limit is length" picks up the hand-off ("short text doesn't carry enough signal")
- Hard red-list variant detects at 16 tokens
- 98.4% detection at z=4 on 200-token generations

#### Paragraph draft
As with any method that relies on statistical tests, the biggest weakness is the "lack of n", *the number of samples*. In this case, that corresponds to the number of tokens in the output. Text watermarks need roughly 25 tokens of high-entropy text to detect reliably; short answers contain very little or no detectable watermark. This is the same problem as detecting a biassed coin: it would be impossible to tell whether a coin is biassed from a single flip, but by the eighth consecutive heads you're fairly certain. According to the Kirchenbauer paper, the hard-variant (strong bias) detects any watermarked sequence with 16 or more tokens with certainty, while the soft variant crosses the z=5 threshold with as few as 35 tokens, and at 200 tokens 98.4% of AI-generated text is detected.

*[Figure 3 adaptation slot — adapted from Kirchenbauer et al., Figure 3(b)](https://arxiv.org/html/2301.10226v4):* average z-score as a function of token length T, simplified to a single δ. Recommendation: **δ = 2, γ = 0.5, multinomial sampling** — the paper's standard soft-watermark setting (used in Figure 1, Table 1, and the 98.4% detection figure). At δ=2 the curve crosses the z=4 detection threshold at roughly 25–35 tokens for high-entropy text, which is exactly the "25 tokens, give or take" claim. Simplification notes for the chart:
- Pick one δ (2.0) and one γ (0.5) — drop the multi-curve comparison; the point is the shape (z grows with √T), not the parameter sweep
- Draw the z=4 threshold as a horizontal line, and mark where the curve crosses it (~25 tokens) — that crossing *is* the section's claim
- Keep the axes honest: T from 2 to 200, z from 0 to ~8
- Caption should attribute: "adapted from Kirchenbauer et al. 2023, Figure 3(b) (δ=2, γ=0.5, multinomial sampling)"
- NB: the paper's own "as few as 25 tokens" claim is for high-entropy text; the curve for low-entropy text sits lower and crosses later — worth a one-line note under the chart, which sets up Length ¶2 (the entropy catch)

✅ **Actual numbers from the paper (resolved — use these instead of the XX.XX% placeholder):**
- **16 tokens, 100% detection (hard variant, theoretical):** §2 — "we will detect any watermarked sequence with 16 or more tokens (the minimum value of T that produces z=4 when |s|G=T)". This is the hard red-list variant where every token is green by construction — the cleanest "actual number" in the paper
- **35 tokens, z > 5 (soft variant, δ=2, 8-way beam search):** §6 — "even for the moderate bias of δ=2, an average z-score greater than 5 is achieved for as few as 35 tokens". z=5 → p-value ≈ 2.9×10⁻⁷ (one-sided), i.e. ~1 in 3.5 million. NB: this is the *beam-search* variant — the figure uses multinomial sampling, so for consistency the section prose should use z=4 (the figure's threshold) and keep the z=5/35-token claim as a footnote with the sampling-scheme caveat
- **128 tokens, 98.4% detection (soft variant, δ=2, multinomial):** §4.1 — "98.4% of generations are detected at the z=4 (128 token) threshold" — this is the empirical detection rate at the z=4 threshold, which occurs at ~128 tokens for the paper's entropy distribution
- **Suggested prose (replaces the XX.XX% placeholder):** "According to the Kirchenbauer paper, the hard variant detects any watermarked sequence of 16 or more tokens with certainty; the soft variant crosses the z=5 threshold at as few as 35 tokens (roughly 1 in 3.5 million odds of a false positive), and at 200 tokens, 98.4% of generations are detected." — three actual numbers, all traceable, no invented percentages
- Note the variant distinction: 16 tokens = hard variant (all-green by construction); 35 tokens = soft variant with beam search; 128/200 tokens = soft variant multinomial. The post's mechanism section describes the soft variant, so lead with 35/128/200 and mention 16 as the hard-variant bound

✅ **Z-score → p-value translation (resolved — yes, but translate to "odds of a false positive", not "certainty"):**
- The translation is mathematically clean because the z-test's p-value is a one-sided tail probability: z=4 → p ≈ 3×10⁻⁵ (3 in 100,000); z=5 → p ≈ 2.9×10⁻⁷ (~1 in 3.5 million). These are exact, not approximations
- **What NOT to do:** don't call the p-value a "certainty percentage". The p-value is the probability that *human* text scores this high by chance — it is NOT "XX% certain this text is AI-generated". That's the prosecutor's fallacy: P(score this high | human) ≠ P(AI | score this high). The paper is careful to call it a false-positive rate, and the post should too
- **Suggested phrasing for the (xx%) placeholder:** "crosses the z=5 threshold at as few as 35 tokens — the odds of human text scoring that high by chance are roughly 1 in 3.5 million" — this is the honest translation: a frequency statement about human text, not a certainty statement about AI text
- Why "1 in 3.5 million" beats "99.99997% certain": the frequency framing is concrete (readers can picture 3.5 million), avoids the prosecutor's fallacy, and matches the paper's own framing ("the probability of a false positive is 3×10⁻⁵" for z=4)
*[Figure 3 adaptation — BUILT: `length-figure.html` at the repo root.](../../length-figure.html)* Adapted from [Kirchenbauer et al., Figure 3(b)](https://arxiv.org/html/2301.10226v4): average z-score as a function of token length T, with a **dropdown for weak / medium / strong bias** (δ = 1 / 2 / 5). γ is fixed at 0.5 and not surfaced in the UI — agreed, since the post hasn't introduced the green-list size parameter; adding it would front-run the mechanism section's dial framing without adding anything the reader needs here. If we later add a γ explainer, the dropdown can gain a fourth option.

**How the dropdown maps to the paper:**
- **Weak (δ = 1)** — crosses z=4 at ~77 tokens. The text reads naturally but the signal is weak; short answers carry almost no detectable watermark
- **Medium (δ = 2)** — crosses z=4 at ~30 tokens. The paper's standard setting (Figure 1, Table 1, the 98.4% figure). This is the "25 tokens, give or take" claim
- **Strong (δ = 5)** — crosses z=4 at ~8 tokens, but a bias this heavy starts to distort the text (the paper reserves δ=5+ for the hardest settings; Table 2 shows no type-II errors at δ=5, γ=0.25)

**Calibration honesty (important):** the curves are *illustrative*, calibrated so medium (δ=2) crosses at ~30 tokens (matching the paper's "as few as 35 tokens" at δ=2 with beam search, and the ~25-token multinomial crossing). The exact curve shapes are interpolations from the paper's reported points, not digitised data — the caption says "illustrative curves based on the paper's reported results". The z=4 threshold line and the 98.4%/200-token figure are exact.

**Y-axis is log-scale (per Marcus):** z runs 0.5 → 20 on a log axis, so the strong-bias curve shows its full shape (up to z≈17 at 200 tokens) without clipping, while the z=4 threshold detail stays visible. Ticks at 0.5, 1, 2, 4, 8, 16. The log scale also makes the √T growth read as a flattening curve, which is the honest shape.

**On consistency: z=4 everywhere (resolved).** The figure's threshold is z=4; the text's "35 tokens, z > 5" claim should be reframed to z=4 for consistency. The paper's numbers at z=4: the threshold is crossed at ~25–35 tokens (δ=2, high-entropy text), and the false-positive rate at z=4 is 3×10⁻⁵ (3 in 100,000). The z=5/35-token claim came from the beam-search variant (§6) — a different sampling scheme from the figure's multinomial. Recommendation: use **z=4 everywhere** in this section (figure + prose), and keep the 35-token/z=5 beam-search claim out of this section or footnote it with the sampling-scheme caveat. The 98.4%/200-token figure is also at z=4, so z=4 unifies all three numbers: ~30 tokens (medium, from the figure), 128 tokens (empirical threshold at the paper's entropy), 200 tokens (98.4%).

**On ROC curves (Figure 4): leave them out of this figure.** Three reasons: (1) this figure's job is the length story — z as a function of T — and ROC answers a different question (detection rate vs false-positive rate at a fixed length); (2) the dropdown already carries the parameter dimension, and adding ROC would make this a two-chart widget; (3) the ROC numbers are in Table 2 and can be cited in prose if needed (98.4% TPR at 1% FPR... actually the paper's Table 2 shows FPR=0.0 empirically at z=4). If we want an ROC visual later, it belongs in the Attack Surface section (where Sadasivan's TPR@1%FPR numbers live) rather than here.

**Dropdown callouts (verified in browser):**
- Weak (δ=1): crosses at ~77 tokens — "the text reads naturally, but the signal is weaker"
- Medium (δ=2): crosses at ~30 tokens — "the paper's standard setting... the '25 tokens, give or take' claim. At 200 tokens, 98.4% of generations are detected"
- Strong (δ=5): crosses at ~8 tokens — "but a bias this heavy starts to distort the text itself"

**On γ (green-list size): agreed, leave it out.** The post hasn't introduced γ, and the dropdown's three biases tell the length story completely. Adding γ would require explaining the green-list size trade-off (smaller γ = stronger watermark but more quality risk, per Figure 2's pareto discussion) — that's Mechanism-section detail, and the dial framing in Mechanism ¶4 already covers it qualitatively ("the bias is a dial"). If a reader wants the parameter sweep, the caption links to the paper's Figure 3.

### Length ¶2
#### Notes
##### Para 2 — the entropy catch.

Low-entropy text (factual answers, names, dates, code) can't be watermarked — the model has no freedom to favour green tokens. Appendix G: factual Q&A is the worst case, weak detection stats, <4-point Exact Match drop.

##### Bullet of points to cover
- Low-entropy text can't be watermarked — no freedom to favour green tokens
- Appendix G: factual Q&A worst case, weak detection stats, <4-point Exact Match drop

#### Paragraph draft
Length isn't the only variable that affects watermarking ability. Entropy is the other key axis: low-entropy text is text that can't be altered without significantly changing its meaning (e.g. factual answers, names, dates, code). Low-entropy text can't be watermarked because the model has no freedom to favour green tokens. The Kirchenbauer paper's own low-entropy example is code, `for(i= 0;i<n;i++) sum+=array[i]`, where the first few tokens strongly determine the following tokens: humans and LLMs will give pretty much the same answer, so there's no statistical gap to detect. If you do force green tokens into it, the quality degrades to the point the code stops working. The figure above assumes high-entropy text; low-entropy text sits lower and crosses the threshold later, if at all. And [Appendix G of the paper](https://arxiv.org/html/2301.10226v4#A7) suggests factual Q&A is the hardest to watermark effectively: low-entropy answers yield weak detection statistics, though quality holds, with Exact Match dropping by less than 4 points for FLAN-UL2 and BLOOMZ on TriviaQA, because the soft watermark passively leaves high-confidence predictions (named entities, factual answers) untouched.

*Proofing note:* the §1.2 code example also appears in the Code ¶1 brief below — when assembling the full draft, keep the verbatim snippet here (it lands the entropy point) and have Code ¶1 reference it rather than re-quote it.

### Length ¶3
#### Notes
##### Para 3 — the builder implication.

Chatbot one-liners and short answers may carry no detectable mark. Don't promise detection you can't deliver; length is a design constraint, not a bug.

##### Bullet of points to cover
- Chatbot one-liners and short answers may carry no detectable mark
- Length is a design constraint, not a bug

#### Paragraph draft
So what does this mean for when we build? If we're building some product that produces short or very deterministic outputs, then watermarking is not a feasible solution. This could be a chatbot for one-liners, or even an AI system using the recently released [Jev](https://en.wikipedia.org/wiki/Jev_(AI_model)). If compliance with [Article 50(2)](https://artificialintelligenceact.eu/article/50/) of the EU AI Act is still a requirement, then there are other methods alongside C2PA metadata that would probably count as "reasonable efforts" (and I'm not a lawyer, so don't take this as legal advice). The easiest would be inserting invisible unicode characters, though a single regex strips them and screenshots destroy them. More complex techniques such as [Adversarial Watermarking Transformers (AWT)](https://arxiv.org/abs/2009.03015) remain at the research stage and aren't production ready. And with respects to Jev: it is a discriminative model that returns probability distributions over choices (text or numbers), so arguably text watermarking doesn't apply to it at all ([System One docs](https://docs.typesafe.ai/concepts/system-one)).

*Proofing notes (this pass):*
1. **"doesn;t"** → "doesn't" (typo)
2. **"article 50(2)"** → linked and capitalised, matching the intro
3. **"best effort" → "reasonable efforts"** — matches the intro's phrasing (the PO's "make reasonable efforts"), so this sentence now answers the intro's question directly. Revert if you prefer "best effort"
4. **Invisible-characters claim fixed for consistency** — "doesn't survive copy and pasting" contradicted Mechanism ¶2's two-layers point (embedded marks survive copy-paste; metadata doesn't). Zero-width characters do survive plain copy-paste (they're in the text); their real weaknesses are sanitisation (one regex strips them) and screenshots. If you meant platform sanitisation, phrase it as "some platforms strip them on paste" (needs verification)
5. **AWT link** → abs form, consistent with the other arXiv links
6. **Jev closer tightened** + System One docs link added on the technical claim
7. **IANAL** → style-guide phrasing ("I'm not a lawyer, so don't take this as legal advice")

*Citation choice (Jev links, resolved):* split the links — "Jev" → Wikipedia (entity context: release date, funding; AI engines ground brand-new entities on Wikipedia, so it's the right target for the entity mention), the discriminative-model sentence → [System One docs](https://docs.typesafe.ai/concepts/system-one) (the vendor states it outright: "System One models do not write replies, produce code, or generate explanations of their reasoning"). GEO engines extract sentences, not links — the link's job is verifiability, so each claim sits next to its best source. SEO impact of either choice alone is negligible.

*Note (Jev, verified):* Jev is a discriminative model — it returns probability distributions over typed choices, not generated text (TypeSafe docs; Forbes/TechCrunch/Register, Sept 2026). So it's not a "short deterministic text" case; text watermarking doesn't apply at all. The sentence now reflects that. Legal wrinkle worth a line in the implementation section: if a system generates no text, Art 50(2)'s marking duty arguably doesn't bite (our reading, not verified).

*Pipeline nuance (Marcus's question):* Jev's `choice` options are string entries, so it *can* select among candidate texts (softmax-like distribution, argmax pick). But the selected text is authored by the candidate source, not generated by Jev — selection isn't generation, so the marking duty doesn't land on the pick (our reading). And there's no token stream to bias: green-list watermarking attaches at generation-time sampling, which a discriminative pick doesn't do. Flip side: if the candidates come from a watermarked LLM, Jev's selection carries that watermark intact (detection works from any contiguous portion) — the pipeline doesn't evade, the duty transfers upstream to the generator.

*Builder implication (follow-up):* generation-time watermarking is only available to whoever controls the sampling; everyone downstream inherits the mark or needs a weaker substitute. If the candidates are unwatermarked (human-written or unwatermarked source), the builder's options: metadata (C2PA — strippable, and whether it satisfies Art 50(2) is unresolved per the PII scenario notes) or post-hoc embedded watermarking (AWT-style learned editing, see Mechanism ¶1 notes — research-grade, quality trade-offs, paraphrase-fragile). If Jev is the whole system (no text output), no duty arguably bites and no watermark is needed. Home for this in the draft: the implementation section or the self-hosted PII scenario. (Draft update: C2PA and AWT are now covered inline in ¶3; the "generation-time belongs to whoever controls the sampling" framing still has a home in the implementation section.) 

## The Attack Surface: What Survives and What Dies

### Attack ¶1
#### Notes
##### Para 1 — direct answer (GEO slot).

"Copy-paste survives text watermarks; paraphrase and translation defeat them."

##### Bullet of points to cover
- One-sentence direct answer, then the sub-sections do the detail

#### Paragraph draft
So what if our text is sufficiently long to carry a detectable watermark? What techniques work against the Kirchenbauer/SynthID method? The tldr is: copy-paste survives the watermark, but paraphrase and translation defeat it.

*Proofing notes (this pass):*
1. **"SynthId"** → "SynthID" (capitalisation, matches the rest of the post)
2. **"embed a watermark" → "carry a detectable watermark"** — precision: the embedding happens at generation regardless of length; length governs *detection* (the length section's claim)
3. **Semicolon before "but"** → comma (a semicolon shouldn't introduce a coordinating conjunction)
4. **"defeats" → "defeat"** (plural subject: paraphrase and translation)
5. **"Copy-paste survives text watermarks" → "copy-paste survives the watermark"** — the original reads as copy-paste being the thing that survives; the intended meaning is the watermark survives copy-paste. Also lowercased after the colon. Alternative if you want to mirror the sub-headings exactly: "copy-paste survives; paraphrase and translation die."
6. **GEO check:** the answer sentence is third, matching the Length ¶1 precedent (bridge first, answer intact and near the top) — extraction still works
7. **Optional:** the tldr omits shortening, the fourth sub-section. The brief scopes this section to copy-paste/paraphrase/translation, and truncation was the length section's story, so leaving it out is defensible; add "and truncation" if you want the tldr to cover all four demo attacks

### Copy-paste survives
#### Notes
Detectable "from only a contiguous portion" of the text — quoting a slice still carries the signal. This is why screenshotting/reposting doesn't help (mirrors the live post's two-layers point).

*Angle (why this isn't redundant with Mechanism ¶2):* the two-layers point is already made, so don't re-explain it. This sub-section's new content: (1) the contiguous-portion property — detection works from any slice of ~25+ tokens, so quoting a paragraph still carries the signal; (2) the criterion framing — copy-paste survives because it leaves the words alone, which is the test every attack has to fail (sets up paraphrase); (3) the screenshot honesty — the words are unchanged so the signal survives, though a detector then needs OCR (our reasoning, not the paper's).

#### Paragraph draft
The Kirchenbauer method survives anything that leaves the words/tokens alone, because the mark lives in the word choices themselves. Copy-pasting an entire document is the obvious case, as is screenshotting. However, the method is stronger than that. Detection works from [any contiguous portion](https://arxiv.org/abs/2301.10226) of the text, so even quoting a single paragraph is enough, as long as it's roughly 25 tokens or more of high-entropy prose. The only way to remove the watermark is to change the words themselves.

### Paraphrase dies (mostly)
#### Notes
Sadasivan et al.: recursive paraphrasing drops detection from 99.3% to 9.7% on 300-token passages; two rounds below 50%. But the nuance: "a few sentences that are partially or not at all paraphrased can be sufficient to trigger detection" — sloppy paraphrase doesn't save you. Quality trade-off: 77% content preservation, 89% grammar rated high-quality.

#### Paragraph draft
So what techniques can actually defeat the watermark? [Sadasivan et al.](https://arxiv.org/abs/2303.11156) tried several attacks that can be best described as paraphrases. Given that the attacker is unlikely to know which tokens are green, the simplest attack is to try and rewrite the outputs, essentially paraphrasing them. This can be done using smaller LLMs that can be run locally (i.e. they won't have their own watermark). This works really well: Sadasivan et al. reported a drop in detection from 99.3% to 9.7% on 300-token passages, and two rounds of paraphrasing are enough to push detection below 50%. Additionally, the content preservation and grammar accuracy still remain high (77% and 89% of paraphrases rated high quality respectively). However, if the paraphrase misses a few sentences that are partially or not at all paraphrased, the detector will still identify those sections, a point Kirchenbauer et al. themselves make.

*Proofing notes (this pass):*
1. **Typos**: "thant" → "that"; "the won't" → "they won't"; "Sadasivian" → "Sadasivan"; "re-write" → "rewrite"
2. **Comma splices/commas**: "This works really well, Sadasivan et al reported..." → colon construction; comma after "green" and after "paraphrased" (last sentence)
3. **"drops to 50%" → "below 50%"** — the paper's claim is "in all the settings pp2 or 2 rounds of paraphrasing is sufficient to degrade TPR@1%FPR to below 50%" (§2.3)
4. **[*is that citeable?*] — YES, resolved and removed.** 99.3% → 9.7% is the paper's intro headline: "recursive paraphrasing attack on watermarked texts, even over relatively long passages of 300 tokens in length, can drop the detection rate (true positive rate at 1% false positive rate or TPR@1%FPR) from 99.3% to 9.7%". Two-rounds-below-50% is §2.3's explicit claim. Both citeable as stated
5. **Numbers added**: 77% content preservation / 89% grammar (the paper's intro headline). NB: the DIPPER-specific figures are 70% / 89% (§2.2, Table 1); 77% is the intro's aggregate across paraphrasers. Since the headline attack uses DIPPER, you could use 70% for tightness — either traces
6. **Attribution added** on the last sentence: the sloppy-paraphrase nuance is Kirchenbauer's (their §6: "a few sentences that are partially or not at all paraphrased can be sufficient to trigger detection"), not Sadasivan's — Sadasivan's attack is the strong recursive one
7. **Link** switched to abs form (post convention)
8. **Precision note (optional tightening)**: the headline 99.3→9.7 uses DIPPER (11B, explicitly trained paraphraser). LLaMA-2-7B-Chat (the locally-runnable one) also works: one round takes TPR@1%FPR from 99.8% to 54.6% (§2.3). So "smaller LLMs that can be run locally" holds, but if you want the claim airtight, name DIPPER for the headline number or drop "run locally". Also "detection" here is TPR@1%FPR (detection rate at 1% false positives) — fine as prose; the figure caption should carry the precise metric

*[Figure adaptation — BUILT: `paraphrase-figure.html` at the repo root.](../../paraphrase-figure.html)* Adapted from [Sadasivan et al., Figure 3(a)](https://arxiv.org/abs/2303.11156): detection rate (TPR@1%FPR) for the soft watermark as paraphrasing rounds proceed, with a **dropdown for DIPPER (11B) / LLaMA-2-7B-Chat (7B)**. Spec (as built):
- Chart: x = paraphrasing round (No attack → 5 rounds), y = detection rate 0–100%, linear. Line + points; filled points = the paper's reported values, hollow points (~) = illustrative interpolations (same calibration honesty as the length figure)
- Citable anchors: 99.3% (no attack, intro headline), 80.7% (pp1, DIPPER, §2.3), below 50% (pp2, §2.3), 9.7% (five rounds, intro headline). LLaMA-2: 99.8% → 54.6% (one round) → below 20% (five rounds)
- Random-detector line at 50% (dashed red), with the two-round crossing ringed and labelled — that crossing is the paragraph's claim
- Quality cost in the callout: perplexity 5.2 → 8.7 (DIPPER) / 10.5 (LLaMA-2), QA accuracy 97% → 95.5% — "slight degradation" is the paper's own framing
- Caption carries the precise metric: "Detection rate is TPR@1%FPR — the true positive rate at a 1% false positive rate"
- Verified in browser: both dropdown views render, labels don't collide, the crossing ring reads clearly

### Translation dies (and the quality risk cuts both ways)
#### Notes
Para 0 — the justification (Marcus's question: aren't translation and paraphrase mathematically the same?): yes — both are semantic-preserving token shifts, and in Sadasivan's TV-distance framework (Corollary 1) they work identically. Don't claim a different mechanism. The justification is *coverage*: the copy-paste section established that any untouched contiguous span of ~25+ tokens still triggers detection (the hash chain matches within the span). Paraphrase is partial — sloppy paraphrase leaves spans, hence "dies (mostly)". Translation is total — every token re-rolled into another language, no untouched span, and the prefix-dependent hash chain diverges at token one, so even shared tokens (names, numbers) land in different green/red contexts. The signal isn't stripped; it was never in the target-language tokens. z collapses to chance. Suggested opening move: "Translation is just a paraphrase into another language — the same token shift, the same mathematics. The difference is coverage: a paraphrase can miss a span, and the last section showed any untouched 25-token span still triggers detection. A translation misses nothing." Secondary differences, one clause each: (1) cross-lingual drift stacks on paraphrase drift (feeds Para 2); (2) the builder angle — translation is a routine localisation step, not an adversarial act, so the mark dies in normal multilingual deployment (compliance problem, not an attack). This gives the section structure a spine: each attack differs by how much of the token stream it leaves untouched (copy-paste: everything; paraphrase: spans; translation: nothing; truncation: a span only if long enough).

*Round-trip nuance (Marcus's follow-up: paraphrase rounds vs one-way translation vs translate-back):* three real differences, and "higher mistranslation risk" is only one. (1) Paraphrase rounds (same language): detection degrades *stepwise* — each round rewrites most tokens but untouched spans survive (99.3 → 80.7 → below 50 → 9.7 over five rounds); quality creeps slowly (perplexity 5.2 → 8.7) because the paraphraser preserves meaning with full context. (2) One-way translation: detection doesn't degrade — it's *out of scope in one pass*: the output is in another language, so the source-vocabulary green list doesn't apply. No iteration needed. (3) Round-trip (translate → translate back): the output returns to the source language so the detector *can* run, but every token has been re-rolled twice — functionally recursive paraphrasing with translation models, two passes instead of five. Mistranslation risk compounds: pass two translates the already-drifted pivot text, so it can't recover what pass one lost, only add drift. But honest framing (feeds Para 2): He et al. removed watermarks "without performance loss" with a good pipeline — quality risk is quality-dependent, not absolute; weak translation models drift far more (Sadasivan's 222M vs 11B DIPPER). Why round-trip exists: one-way changes the language (fine for localisation, useless if the audience reads English); round-trip restores the language while killing the mark. He et al.'s CWRA is the generation-time cousin (generate in pivot, translate to target). Home: Para 0 lands the coverage story; this nuance feeds Para 2's quality-risk angle.

Para 1: He et al. 2024 (ACL 2024, [arXiv:2402.14007](https://arxiv.org/abs/2402.14007) — "Can Watermarks Survive Translation? On the Cross-lingual Consistency of Text Watermark for Large Language Models"): current watermarks "lack consistency" across languages; CWRA (generate in a pivot language, translate) drops AUC to random-guessing. Both claims verified against the abstract.

Para 2 — the mistranslation angle (your addition): the attacker inherits a quality risk. Smaller/weaker translation models drift more (Sadasivan's 222M paraphraser degraded far more than 11B DIPPER). But honest framing: He et al. achieved removal "without performance loss" with a good pipeline — so the risk is quality-dependent, not absolute.

Metaphor slot — the Bible translation analogy (yours to finalise): English versions differ depending on whether they trace to the Masoretic text or the Septuagint — same "source", different words, some renderings lose more in transit. Scope: OT, "different textual traditions" not "mistranslation". Use for the attacker's quality risk only.

#### Paragraph draft
The biggest gap with paraphrasing is that not all of the text gets changed, meaning you run the risk of letting a significant number of the green tokens through. So what's truly needed is a way to change *all* the tokens without changing the meaning. The best way to do this is to translate the text, and then optionally translate it back. [He et al. 2024](https://arxiv.org/abs/2402.14007) showed that current watermarks aren't consistent across languages and that with their carefully built pipeline they were able to remove the watermark without performance loss, dropping detection to random-guessing levels. However, unless you want to operate in that second language, you'll have to translate it back to the original language. This means that your outputs are going through another round where the meanings could be altered.

However, there is a real cost here for both paraphrasing and translation. For most people, your choice is to either; spend more tokens for the same output (each round costs), or, you could run a smaller model locally which runs the risk of being less accurate, particularly if you have a large piece of text and the context window fills.

*Proofing notes (this pass):*
1. **Citation filled and verified:** [He et al. 2024](https://arxiv.org/abs/2402.14007) — "Can Watermarks Survive Translation? On the Cross-lingual Consistency of Text Watermark for Large Language Models" (Zhiwei He et al., ACL 2024 main conference). Both claims trace to the abstract: current watermarking technologies "lack consistency when texts are translated into various languages", and CWRA removes watermarks "decreasing the AUCs to a random-guessing level without performance loss". (The earlier ID guesses were one digit off — 2402.14057 is a graphene paper; this is 2402.14007.)
2. **"do not remain consistently across languages" → "aren't consistent across languages"** — "remain" takes an adjective, not an adverb; contraction per the style guide. The paper's phrasing is "lack consistency", so this is a fair gloss.
3. **"letting a significant number of the green tokens getting through" → "letting a significant number of the green tokens through"** — after "letting", the bare infinitive is correct; drop "getting".
4. **"However there is" → "However, there is"** (comma after the introductory adverb).
5. **"for both paraphrasing and translations" → "for both paraphrasing and translation"** (singular, parallel with "paraphrasing").
6. **"For most people your choices are to either spend more tokens... or you could run a smaller model locally"** — mixed construction ("choices are to X or you could Y"). Suggest: "For most people, the choice is between spending more tokens for the same output (each round costs) or running a smaller model locally, which risks being less accurate, particularly if you have a large piece of text and the context window fills." Also comma after "For most people". NB in the latest revision the punctuation became "to either; spend... (each round costs), or, you could" — the semicolon after "either" and the comma after "or" should both go; the rewrite above absorbs them.
7. **"unless you want to operate in that second language you will have to" → "unless you want to operate in that second language, you'll have to"** (comma closing the subordinate clause; contraction).
8. **Applied:** the headline stat is now in — "dropping detection to random-guessing levels". Traces to the paper's abstract ("decreasing the AUCs to a random-guessing level without performance loss"); AUC 0.5 is a coin flip, which matches the paraphrase figure's "Random detector (50%)" line, so the vocabulary is consistent across sections.
9. **Optional tie-back:** "not all of the text gets changed" could sharpen to the copy-paste section's criterion — any untouched contiguous span of ~25+ tokens still triggers detection, so even one unparaphrased paragraph leaks. One clause would connect the two sections and explain *why* partial paraphrase leaks.
10. **Citation scope check (no misattribution):** He et al.'s CWRA is one-way — generate in a pivot language, then translate to the target. Your "optionally translate it back" is your own framing and sits in the previous sentence, so the citation isn't over-claimed. Fine as is.
11. **Redundancy check (second paragraph):** the paraphrase figure's callouts already carry the perplexity/quality costs, but this paragraph's angle is different — the attacker's compute trade-off, and the context-window point is new. It fits the heading ("the quality risk cuts both ways"), but the pending compute-cost section may want it — decide when you draft that section.
12. **Optional:** "So what's truly needed" — the previous section opens "So what techniques can actually defeat the watermark?", so that's two "So" openers in a row; consider "What's needed is...". "Truly" is also doing little work.

### Shortening dies
#### Notes
Truncate below ~25 tokens and the signal is gone. The demo shows all four attacks.

*Angle (why this isn't redundant with the length section):* the length section made the builder's point (short outputs carry no mark); this sub-section makes the attacker's point (cutting a watermarked document down defeats detection). Same threshold, two different stories. The mechanism: truncation doesn't change any words — the surviving tokens still carry the mark (the contiguous-portion property from the copy-paste section) — so shortening doesn't strip the signal, it starves the test. The z-score grows with √T (established in the length figure), so halving the tokens weakens the signal by roughly 30%; below ~25 tokens of high-entropy text it can't clear z=4.

*The conditional (the honest framing):* "dies" is only true below the threshold. Quote a 200-token excerpt and detection still works (98.4% at 200 tokens, from the length section). So the attack is truncation *below ~25 tokens*, not truncation per se — parallel to "Paraphrase dies (mostly)". Optional heading tweak to match the pattern: "Shortening dies (below the threshold)".

*The LLM-shorten wrinkle (Marcus's question: does "LLM, shorten this to 25 words or fewer" count as paraphrase or shortening?):* it's a paraphrase-class attack wearing a shortening label — the taxonomy is about how much of the original token stream survives, not what the operation is called. Three senses of "shorten": (1) pure truncation (delete everything after token ~25) — surviving tokens are original, the hash chain matches within the span, detection works if the span is long enough (the demo's Shorten attack); (2) extractive shortening (keep 2-3 original sentences verbatim) — same conditional survival, judged per sentence; (3) abstractive shortening ("LLM, shorten this to 25 words") — the LLM generates fresh text, almost no original tokens survive (a quoted name or number is 1-5 tokens, far below the ~25-token contiguous span the z-test needs), so the signal wasn't diluted, it was never in the new tokens — functionally identical to translation. It's the strongest attack in the set: total rewrite (translation-class coverage) plus compression. Supporting detail: this is the operation the withdrawn CLSA paper studied (arXiv:2510.24789, "Cross-Lingual Summarization as a Black-Box Watermark Removal Attack" — withdrawn for lacking length controls, i.e. it couldn't isolate the rewrite effect from the shortening effect, which itself shows the two are recognised as distinct mechanisms). Words/tokens care (the Mechanism NB): 25 words ≈ 30-40 tokens, which would clear the threshold IF the tokens were original — but an LLM rewrite means they aren't. One clause in the prose sharpens the demo's definition: "shortening" here means cutting the original down (the tokens survive); asking an LLM to rewrite-and-compress is a paraphrase (they don't).

*The spine completes here:* copy-paste leaves everything (survives); paraphrase leaves spans (mostly dies); translation leaves nothing (dies); truncation leaves a span only if it's long enough (conditional). One closing clause naming the shared test — how much of the token stream survives — hands off to the Code Blindspot (the case where the stream can't be marked in the first place).

*Entropy caveat (one clause):* where the threshold sits depends on entropy (Length ¶2) — a 30-token excerpt of low-entropy text won't detect; a 30-token excerpt of high-entropy prose might. No hard line; "roughly 25 tokens of high-entropy text" is the honest phrasing.

*Demo note:* attack-matrix.html's Shorten row says "⚠️ Degraded — too few tokens to detect reliably", which is the right framing: the signal is still in the surviving tokens, there's just too little of it. Placement question: the matrix covers all four text attacks (plus the image ones) — end of this section as the attack-surface closer, or after Attack ¶1? End-of-section reads better: prose → four sub-sections → the matrix summarises them.

#### Paragraph draft
The final attack is to shorten the text. And there are three ways to do this.
1. Simply cut off everything after 25 tokens.
2. Just keep 2-3 sentences verbatim
3. Ask the LLM to "shorten this to 25 words or fewer". This is a hybrid of the paraphrasing and shortening, and it's the most effective: re-rolling every token means the signal is never in the new text, while the compression removes the leftover spans a sloppy paraphrase would leave behind.

If the shortening takes the text below roughly 25 tokens of high-entropy prose, the watermark becomes hard to detect reliably. However, if the text is high-entropy, it may still be detectable, and in a short length of text there is only a certain amount of information you can convey. At some point, *the juice isn't worth the squeeze*. That's the test every attack in this section shares: how much of the token stream survives. The next section covers the one case where the stream can't be marked in the first place.

*Proofing notes (this pass):*
1. **Item 1 dropped — resolved.** The list is now three attacks on existing watermarked text, which is the right scope; the builder's generation-time choice lives in Length ¶3.
2. **Applied:** "The final form" → "The final attack" is in. Still carried over: "three possible ways" — "possible" does little work.
3. **Applied directly:** the hybrid clause now shows why it's the most effective — "This is a hybrid of the two, and it's the most effective: re-rolling every token means the signal was never in the new text, while the compression removes the leftover spans a sloppy paraphrase would leave behind." ("alongside" → "of the two", full stop added, claim shown not asserted.)
4. **Applied directly:** "effective" is now defined — "If the shortening takes the text below roughly 25 tokens of high-entropy prose, the watermark becomes hard to detect reliably."
5. **Applied — C′ dropped (Marcus's call):** agreed, it's the right call. The draft's existing "if the text is high-entropy it may still be detectable" carries the conditional, and the paragraph goes straight to the utility cost. The threshold callback lives in the length section where it belongs; the 98.4%/200-token figure stays retired from this section.
6. **Applied:** "visible" → "detectable" is in, and the double "still" is gone. Comma after "high-entropy" still wanted: "However, if the text is high-entropy, it may still be detectable".
7. **Applied — but the fix introduced a duplication:** "and in a short length of text there is only a certain amount of information you can convey in a short length of text" — "in a short length of text" now appears twice. Suggest: "and there's only so much information you can convey in a short text".
8. **Applied:** comma in "At some point, the juice isn't worth the squeeze" is in, and the quote is closed. Optional: the quotation marks around the idiom can go — "At some point, the juice isn't worth the squeeze." reads cleaner without them, and it's an idiom rather than a quotation.
9. **Applied directly:** the hand-off clause is in — "That's the test every attack in this section shares: how much of the token stream survives. The next section covers the one case where the stream can't be marked in the first place." The section spine completes: copy-paste leaves everything, paraphrase leaves spans, translation leaves nothing, truncation leaves a span only if long enough — and code can't be marked at all.
10. **Demo placement (carried over):** attack-matrix.html at the end of this section as the attack-surface closer; its Shorten row ("⚠️ Degraded — too few tokens to detect reliably") already frames it correctly.

## The Code Blindspot

### Code ¶1
#### Notes
Code is "text" under Art 50(2) — but it's practically unwatermarkable: low entropy, any token change breaks it. The Kirchenbauer paper's own low-entropy example is code: `for(i= 0;i<n;i++) sum+=array[i]`.

##### Bullet of points to cover
- Docstring nuance (Marcus's take, not paper-backed): code itself is unwatermarkable, but docstrings and comments are natural language with real entropy — the model has genuine freedom there, so they could carry a mark. Honest caveat: the z-test counts green over whatever you feed it and can't tell signal tokens from chance-level tokens, so a whole-file detection dilutes the docstring signal — the ~900 chance-level code tokens swamp the ~100 docstring tokens (z ≈ 0.3 instead of z ≈ 4 on a 1000-token file). Reconciliation with the contiguous-portion property (Marcus's question): that property is about running the detector on a CLEAN sub-span; dilution is about a MIXED input. The escape hatch: extract the docstrings and detect on that span alone — but it needs ≥~25 contiguous high-entropy tokens and you'd have to know to extract them; a naive whole-file detector won't. Same dilution continuum as sloppy paraphrase (§6): some chance-level tokens → z reduced but maybe still above threshold; a code file is the extreme → signal drowns. Flag as our reasoning, not a paper claim.

#### Paragraph draft
According to [Article 50(2)](https://artificialintelligenceact.eu/article/50/) code could be considered as 'text'. However, as code is low-entropy e.g. `for(i= 0;i<n;i++) sum+=array[i]` can only be written in so many ways. Which means there is no statistical gap for a detector to exploit, and unlike prose you can't force green tokens without breaking it. Docstrings and long comments are exemptions: they're natural language with real entropy, so the model has genuine freedom and could theoretically carry a mark. However, to detect the watermark you would probably have to exclusively assess the docstring or comment (which would also need to be over 25 tokens) as if you feed in the whole file, the watermark will likely be diluted by the code. As a caveat I'm not aware of any research on this, so treat this as speculation rather than facts.

*Proofing notes (this pass):*
1. **Applied:** the empty link is filled, the length-section example is referenced (not re-quoted), the docstring caveat is in, and the honest-uncertainty closer is in — "I'm not aware of any research on this, so treat this as speculation rather than facts" lands the revisit-list item correctly.
2. **Applied:** the whole-file dilution is now in the draft — "as if you feed in the whole file, the watermark will likely be diluted by the code" — and the escape hatch ("you would probably have to exclusively assess the docstring or comment") carries the reconciliation with the contiguous-portion property. The parenthetical "(which would also need to be over 25 tokens)" is the right conditional.
3. **REVISED (Marcus is right — the suggested opening over-claimed):** "Code is 'text' under the EU AI Act" asserts as settled fact what the Act never addresses — Art 50(2) requires providers of AI systems generating synthetic "text content" to mark outputs, and says nothing about code. "Could be considered" is the honest hedge, and it's load-bearing: Code ¶2's whole point is "the EU hasn't addressed this", so asserting "is 'text'" in ¶1 would set up ¶2 to walk it back. Keep the attribution. The GEO fix is to add the payload, not drop the hedge: "According to Article 50(2), code could be considered 'text' — but it's practically unwatermarkable." (Also drop "as" from "considered as" — non-standard.) Consistency flag: the exec summary bullet says "code is 'text' under the Act" — same over-claim; decide whether the compression is acceptable or the bullet wants "arguably" too.
4. **"However, as code is low-entropy e.g. `for(i= 0;i<n;i++) sum+=array[i]`, there is..."** — comma after "low-entropy" before the e.g. clause; "e.g." mid-sentence reads awkwardly — "— for example, `for(i= 0;i<n;i++) sum+=array[i]` —" or "such as". Also "exploit" → "find" (the gap isn't an exploit, it's a signal absence — "exploit" implies an attack, which is the next section's frame).
5. **"Docstrings and long comments are exemptions"** → "the exception" (singular — they're one exception to the code rule, not multiple exemptions; "exemptions" also carries legal connotations that clash with the Art 50(2) framing).
6. **"the model has genuine freedom and could theoretically carry a mark"** — dangling: the model doesn't carry the mark, the docstrings do. Suggest: "the model has genuine freedom there, so they could theoretically carry a mark".
7. **"you would probably have to exclusively assess"** — adverb placement: "exclusively assess" reads as "assess exclusively"; suggest "assess the docstring or comment exclusively" or "assess only the docstring or comment". Also "probably" + "would" is double hedging — "you'd likely have to".
8. **"as if you feed in the whole file, the watermark will likely be diluted by the code"** — comma before "as" (it's a causal clause, not "as if"); "will likely" → "is likely to be"; "diluted by the code" → "diluted by the chance-level code tokens" (precision: it's not the code diluting, it's the code tokens landing green at chance).
9. **"As a caveat I'm not aware"** → comma after "As a caveat"; "speculation rather than facts" → "reasoning rather than a result" (parallel singular; "speculation" undersells it — it's reasoned from the mechanism, just untested).
10. **¶1/¶2 scope check (carried over):** the "shipping AI-generated code to clients" framing is Code ¶2's setup (the legal gap). This draft is now purely the technical story — good; the EU-hasn't-addressed-it point lives in ¶2.
11. **GEO check (revised per item 3):** the first sentence should carry both halves — the sourced hedge AND the payload. "According to Article 50(2), code could be considered 'text' — but it's practically unwatermarkable." extracts cleanly and doesn't over-claim. The draft's current opening states the legal claim but not the section's takeaway, so GEO extraction of sentence one alone misses the "unwatermarkable" half.

### Code ¶2
#### Notes
The EU hasn't addressed this. If you ship AI-generated code to clients, the marking duty technically applies and the technical solution doesn't exist. Flag honestly: this is a gap, not a loophole you should exploit. (The live post's Business Insider developer quote about AI labels on client code lands here.)

*Angle (why this isn't redundant with ¶1):* ¶1 is the technical story (code is low-entropy, docstrings are the exception); ¶2 is the legal story (the duty applies, the solution doesn't). The new content: (1) the gap framing — the Act's marking duty technically bites on AI-generated code, but no watermarking technique works on it, so "reasonable efforts" has no technical answer here; (2) the honesty flag — this is a gap in the legislation, not a loophole to exploit; shipping unmarked AI-generated code to EU clients is a compliance risk, not a clever workaround; (3) the developer quote slot — the live post's Business Insider quote about AI labels on client code lands here as the practitioner's voice.

*Structure (three moves):* (1) the duty applies — Art 50(2) makes no code/text distinction, so a provider shipping AI-generated code to EU clients is arguably in scope; (2) the solution doesn't exist — ¶1 established why (low entropy, docstring dilution), so "reasonable efforts" has nothing to point at; (3) the honest flag — name the gap, don't exploit it. Keep tight, link out for the legal specifics (the PII scenario's Para 3 covers Art 50(2) scope in depth — don't re-explain here).

**Example (work off this):**

"Here's the gap: Article 50(2) makes no distinction between text and code, so if you're shipping AI-generated code to EU clients, the marking duty arguably applies to you. But as the last section showed, no watermarking technique works on code — the signal has nowhere to live. The Act asks for 'reasonable efforts' as far as technically feasible, and for code the honest answer is that the state of the art doesn't have one. That's a gap in the legislation, not a loophole: shipping unmarked AI-generated code is a compliance risk you're accepting, not a workaround you've found. As one developer put it [Business Insider quote slot], the labels clients ask for don't exist for code yet."

*Drafting notes for the example:*
- "arguably applies" keeps the hedge (same register as ¶1 — the Act never addresses code)
- "as the last section showed" ties ¶2 to ¶1 without re-explaining the entropy argument
- The "reasonable efforts" callback resolves the intro's hook (the PO's shrug) — the Act is more specific than the shrug suggested, but for code it still has no answer
- "a gap, not a loophole" is the honesty flag the notes call for — it's the post's register, and it protects the reader from treating the gap as advice
- The quote slot needs the actual Business Insider quote verified before publishing (the live post has it)

#### Paragraph draft
Here's a genuine gap in the the Act: [Article 50(2)](https://artificialintelligenceact.eu/article/50/) makes no distinction between text and code. So if you're shipping AI-generated code to EU clients, the marking requirement arguably applies. The enforcement chain goes from the EU Commission → EU AI Office → National Authorities → Courts. This means the Commission would have the first words, but ultimately the national(?) courts within an EU jurisdiction have the final say, and given the civil law nature of the EU it could be on a case-by-case basis. For example, if you're building a vibe-coding platform similar to [Lovable](https://lovable.dev/), the documentation you attach as docstrings to the code might be seen as requiring a watermark. This could actually be seen as the responsible thing to do as your end users are likely non-technical and so won't know how to watermark outputs themselves, whereas someone shipping code to load a `model.bin` as part of a wider workflow has nothing to mark. 

Regardless, the Act asks for 'reasonable efforts' as far as technically feasible, and the honest answer is, as of October 2026, there isn't a reliable method of watermarking code. However, the moment it becomes technically possible you could be required to watermark it, I'm not a lawyer so treat this more as reasoning rather than legal advice, and as the Act is still in flux it's best to check with the Commission's own [EUR-Lex](https://eur-lex.europa.eu/eli/reg/2024/1689/oj).

*Proofing notes (previous pass):*
1. **Typos:** "in the the Act" → "in the Act"; empty link → [Article 50(2)](https://artificialintelligenceact.eu/article/50/); "loveable" → "Lovable" (the company's styling). --> Done
2. **Comma splice:** "a genuine gap in the Act, [Article 50(2)] makes no distinction" — the second clause is a new sentence: "And here's a genuine gap in the Act: [Article 50(2)](https://artificialintelligenceact.eu/article/50/) makes no distinction between text and code." (colon construction, matching the paraphrase section's pattern). --> Done
3. **"Ultimately the interpretation will lie with the EU Commission and given the civil law nature of the EU it could be on a case by case basis."** — comma before "and given" (compound sentence); "case by case" → "case-by-case" (compound adjective); "Ultimately" does little work. Also the claim needs a hedge: the Commission issues guidelines and the AI Office enforces, but interpretation ultimately lands with courts — suggest "the interpretation will likely lie with the EU Commission and, given the civil law nature of the EU, could be decided case by case". NB this is our reading, not verified — worth an IANAL-adjacent hedge or a link to the Commission's guidelines page. --> Mostly done, but who ultimately makes the decision? I don't know and I still need the IANAL option. **Answer (our reading, not verified):** the enforcement chain is Commission → AI Office (guidelines, market surveillance) → national authorities → courts. For an interpretation question like "does code count as text content?", the Commission's guidelines would be the first word, but only courts give the final one — and until either speaks, it's genuinely open. The honest phrasing: "The interpretation will likely start with the EU Commission's guidelines, but until a court or the AI Office rules on it, it's genuinely open — and I'm not a lawyer, so don't take this as legal advice." That lands the IANAL hedge (matching Length ¶3's phrasing) and the honest uncertainty in one sentence. --> Amended
4. **The Lovable example — your clarified point is better than my suggested rewrite.** "if you make a system that allows people to 'vibe-code' then the responsible thing would be to make sure it is as watermarked as possible. Especially, as the non-technical people building are unlikely to know how to watermark" — that's the *responsibility* angle: the platform operator owes the watermarking because its users can't do it themselves. That's a stronger point than the entropy contrast (which ¶1 already made). Suggested phrasing: "if you're building a vibe-coding platform similar to Lovable, the responsible thing is to watermark as much of the output as possible — especially since the non-technical people building on it are unlikely to know how." The `model.bin` contrast still works as the second half (nothing to mark), but the responsibility angle is the new content. --> I think the point I was making was that if you make a system that allows people to "vibe-code" then the responsible thing would be to make sure it is as watermarked as possible. Especially, as the non-technical people building are unlikely to know how to watermark. --> Improved
5. **"Regardless, the Act asks for 'reasonable efforts' as far as technically feasible - and the honest answer is as of October 2026 there isn't a reliable method of watermarking code."** — the hyphen before "and" renders as a dash (style guide: no em-dash defaults; use a comma or split); comma after "the honest answer"; "as of October 2026" is a good concrete date (keep — it dates the claim honestly). Suggest: "Regardless, the Act asks for 'reasonable efforts' as far as technically feasible, and the honest answer, as of October 2026, is that there isn't a reliable method of watermarking code." --> Done
6. **"the moment that it becomes technically possible"** → "the moment it becomes technically possible" (drop "that"); "you could then be required to ship" — "then" does little work; "ship" is ambiguous (ship what? the watermark? the code?). Suggest: "However, the moment it becomes technically possible, you could be required to watermark it." --> Done
7. **The "gap, not a loophole" honesty flag — Marcus's call, and he's right:** the draft never explains how the gap could be seen as a loophole, so asserting "not a loophole" would raise the question it answers. Drop it. The paragraph's existing register ("the honest answer is...") already carries the honesty flag without the label. --> I'm not sure this is necessary, and I haven't explained how it could be seen as a loophole.
8. **Business Insider quote — DROPPED from this paragraph (Marcus's call, and he's right):** the verified quote is **Vladislav Rajtmajer, a freelance developer in the Czech Republic** (["Claude users are canceling their subscriptions, citing Anthropic's new AI watermark"](https://www.businessinsider.com/claude-users-cancel-subscriptions-citing-anthropic-new-ai-watermark-2026-8), Thibault Spirlet, 15 Aug 2026; full notes in [bi-claude-watermark-article-notes.md](bi-claude-watermark-article-notes.md)): he "worried an AI label on code shipped to clients could raise questions about authorship or trigger contract penalties." **Why it doesn't fit here:** the paragraph's claim is "the duty applies but can't be satisfied" (no reliable method exists); Vlad's worry is about the *consequences of a mark being present*. Citing him would raise the contradiction — a reader would think "if code can't be watermarked, why is this developer worried about a label on his code?" The quote argues against the paragraph. **Nuance (Vlad is imprecise, not unjustified):** (1) code never ships as pure code — docstrings, comments, commit messages, PR descriptions are natural language with real entropy and CAN carry a detectable mark (¶1's escape hatch); (2) the contract-penalty risk doesn't depend on detection at all — it depends on contractual AI-use clauses. So his fear is real but imprecise. **Better homes if wanted:** the intro hook (market fear is real — developers cancelling $100/month subscriptions over watermark uncertainty is the flip side of the PO's "how do we comply" shrug) or the Builder Bottom Line (the market consequence of the gap). The Echols quote ("Even if you edit your own work that you wrote, they add the watermark anyway") DOES have a natural post-3 home: the paraphrase section's light-edit survival point. The paragraph stands without any quote — it already carries the legal argument, the Lovable responsibility angle, and the dated honest answer.
9. **"could be interpreted as applying"** — fine hedge (consistent with ¶1's register), but "interpreted as applying" is slightly awkward; "could be read as applying to you" or "arguably applies" (the example's phrasing) reads cleaner. --> ok changed
10. **GEO check:** the first sentence is the gap framing — good, but it starts with "And here's" which won't extract cleanly. Suggest: "Here's the gap: Article 50(2) makes no distinction between text and code." (colon construction, drops the "And" opener — the previous section ends on the hand-off, so this section can open clean). --> Done
11. **¶1/¶2 hand-off check:** the Shortening section's hand-off promised "the one case where the stream can't be marked in the first place" — ¶1 delivered the technical story; ¶2's "And here's a genuine gap" picks up the thread. The "And" opener is defensible as a continuation, but the colon construction in item 2 achieves the same link more cleanly. --> Ok think I'm done.

*Proofing notes (this pass — the latest revision):*
1. **The enforcement chain renders as raw markdown:** "The enforcement chain goes from the EU commission --> EU AI Office --> National Authorities --> Courts" — the `-->` arrows will render as literal text (and `>` starts a blockquote in markdown). Prose needs words: "The enforcement chain runs from the EU Commission through the AI Office and national authorities to the courts." Also "commission" → "Commission" (capitalisation, matching the rest of the post).
2. **"the commission would be the first words"** → "the Commission would have the first word" (idiom; "first words" reads as a typo). Also "This means" does little work — the sentence can start directly: "The Commission would have the first word, but ultimately the courts have the final say".
3. **"would have the final say" → "have the final say"** (present tense for a standing fact; "would" implies a hypothetical).
4. **"This could be actually be seen"** → double "be" (typo): "This could actually be seen". Also "could actually" — "actually" does little work; "This could be seen as the responsible thing to do".
5. **"as your end users are likely non-technical and so are unlikely to know"** — "likely... unlikely" reads awkwardly; "as your end users are likely non-technical and won't know how to watermark outputs themselves" or "since your end users are probably non-technical and unlikely to know how".
6. **"Whereas someone shipping code..."** — sentence fragment ("Whereas" makes it subordinate); join to the previous sentence with a comma or start fresh: "By contrast, someone shipping code to load a `model.bin` as part of a wider workflow has nothing to mark."
7. **The IANAL hedge — Marcus's question: is a second carve-out worth it, or does it hurt the flow?** Your flow concern is right — Length ¶3 already carries the full disclaimer ("I'm not a lawyer, so don't take this as legal advice"), and repeating it verbatim two sections later reads as boilerplate. But this paragraph makes the strongest legal claim in the post (who interprets the Act, whether the duty applies to code), so *some* hedge belongs here. The draft's existing closer already does the work: "I am not a lawyer so this is not definitive and as the AI Act is still in flux it is always best to check with the commission itself" — that's the right register (hedge + practical advice), it just needs tightening. Suggested: "I'm not a lawyer, so treat this as reasoning rather than legal advice — and as the Act is still in flux, it's always best to check the Commission's own guidance." Placement at the end is right: the disclaimer lands after the legal claim it hedges, and it doesn't interrupt the flow mid-paragraph. A start-of-post disclaimer would be too far from the claim it covers.
8. **The Business Insider quote — refresh: is it worth including?** The verified quote is **Vladislav Rajtmajer, a freelance developer in the Czech Republic** (["Claude users are canceling their subscriptions, citing Anthropic's new AI watermark"](https://www.businessinsider.com/claude-users-cancel-subscriptions-citing-anthropic-new-ai-watermark-2026-8), Thibault Spirlet, 15 Aug 2026; full notes in [bi-claude-watermark-article-notes.md](bi-claude-watermark-article-notes.md)): he "worried an AI label on code shipped to clients could raise questions about authorship or trigger contract penalties." **My take: it adds real value, and this is the right sentence for it.** Three reasons: (1) it's the practitioner's voice on exactly this paragraph's claim — a real developer worried about the same authorship/contract risk the paragraph describes, which turns our reasoning into observed behaviour; (2) it dates the concern honestly (Aug 2026, right after Anthropic's watermark went live 2 Aug) — the concern isn't hypothetical, it's already happening; (3) it's the only external evidence in the paragraph, and the style guide prizes concrete evidence. Suggested placement after the "reasonable efforts" sentence: "As one freelance developer told Business Insider, an AI label on code shipped to clients could 'raise questions about authorship or trigger contract penalties.'" (reported speech + short direct quote, per the citation caution — the passage is reported speech, so don't present it as a verbatim quotation). If it feels like stacking, the alternative home is the Builder Bottom Line — but the quote is about code-to-clients specifically, which is this paragraph's frame.
9. **Optional:** "Here's a genuine gap in the the Act" — the doubled "the" is still there (item 1 of the previous pass marked it Done but the text still reads "in the the Act").
10. **The closer needs a comma splice fix:** "you could be required to watermark it, I am not a lawyer so this is not definitive" — comma splice; split or semicolon: "However, the moment it becomes technically possible, you could be required to watermark it. I'm not a lawyer, so this isn't definitive..." Also "I am" → "I'm" (contraction, style guide); "check with the commission itself" → "check the Commission's own guidance" (capitalisation; "with... itself" is awkward).

## Implementation: SynthID Text in Your Stack

### Implementation ¶1
#### Notes
##### Para 1 — direct answer (GEO slot).

"SynthID Text is applied at generation time as a logits processor — you need logits access, which means self-hosted weights or an API that exposes logit biasing."

Quote slot (resolves the hook's vagueness): the Act's actual text — outputs must be marked "in a machine-readable format and detectable as artificially generated or manipulated", with solutions "effective, interoperable, robust and reliable as far as this is technically feasible, taking into account... the costs of implementation and the generally acknowledged state of the art" ([Art. 50(2)](https://artificialintelligenceact.eu/article/50/)). More specific than the PO's shrug suggested — and still no how. That's what this section is for.

*Bridge from Code ¶2 (flow fix, same pattern as Length ¶1 and Attack ¶1):* Code ¶2 ends on "the moment it becomes technically possible, you could be required to watermark it" — Implementation ¶1 should pick up the thread: for text, it's already technically possible. Suggested bridge: "For text, though, the how already exists." Then the direct answer lands as the second sentence — GEO extraction still works because the answer is intact and near the top.

*Structure (three moves):* (1) the bridge — for text the how exists; (2) the direct answer (GEO slot) — SynthID Text, generation time, logits processor, logits access required; (3) the Act quote — resolves the intro's hook (the PO's "make reasonable efforts" shrug): the Act is more specific than the shrug suggested ("effective, interoperable, robust and reliable as far as this is technically feasible, taking into account... the costs of implementation and the generally acknowledged state of the art") but still gives no how — which is what this section delivers.

*Angle (why this isn't redundant with Mechanism ¶2):* the mechanism section explained how green-list watermarking works in the abstract (Kirchenbauer's scheme); this section is the production implementation (SynthID Text) and the builder's actual decision: where it sits in your stack, what access you need, what you can and can't do. New content: the logits-access requirement (self-hosted weights or an API exposing logit biasing), the HuggingFace integration, and the closed-API limitation (¶3).

*Section spine (three paragraphs):* ¶1 = the what and where (generation time, logits access); ¶2 = the how (HuggingFace `watermarking_config`, code snippet); ¶3 = the limits (can't watermark a closed API you don't control). The compute cost and Security sub-sections follow as operational detail.

#### Paragraph draft
So how do you implement text-embedded watermarks? The open-source production implementation is Google's [SynthID Text](https://deepmind.google/models/synthid/), which is applied at generation time as a logits processor (you need logits access to the model either through self-hosted weights or an API that exposes logit biasing). The Act is more specific than the Product Owner's shrug suggested: it asks for solutions that are "effective, interoperable, robust and reliable as far as this is technically feasible" ([Art. 50(2)](https://artificialintelligenceact.eu/article/50/)). Thankfully, this is fairly easy. DeepMind and Hugging Face provide a [guide](https://huggingface.co/blog/synthid-text), and the integration is included in the `transformers` library (v4.46.0 onwards), see the example below:

*Proofing notes (this pass):*
1. **Quote verified against Art. 50(2):** "effective, interoperable, robust and reliable as far as this is technically feasible" is an exact substring of the Act's text (the full sentence continues "...taking into account the specificities and limitations of various types of content, the costs of implementation and the generally acknowledged state of the art, as may be reflected in relevant technical standards"). The one-clause quote is fair as stated.
2. **"at generation" → "at generation time"** — the standard phrase; "at generation" reads clipped.
3. **"The open-source implementation" → "The open-source production implementation"** — Kirchenbauer's reference implementation is also open source, so the bare definite article slightly over-claims; "production" scopes it and matches Mechanism ¶1's framing ("the production implementation that followed in Nature").
4. **"in the story above" cut** — "more specific than the Product Owner's shrug suggested" is tighter and the reader already knows who the PO is. Revert if you want the explicit anchor.
5. **Trailing space after the final citation** removed.
6. **GEO check: fine.** The answer payload (SynthID Text, generation time, logits processor, logits access) lands in sentence two, matching the post's question-first precedent (Length ¶1, Attack ¶1) — extraction still works.
7. **Pattern note for the final assembly pass:** "So how do you implement…" is the sixth "So" opener in the post (Mechanism ¶2, Length ¶3, Attack ¶1, Paraphrase, Translation, this). Not a must-fix here, but worth a sweep when the full draft is assembled.
8. **deepmind.google link is the right choice** — Mechanism ¶1 already links Nature; this section is about the product a builder would actually use.
9. **Housekeeping:** the `##### Old draft` subsection can go when the full post is assembled.

*Proofing notes (bridge tweak, this pass):*
1. **"where you can also download the transformers" → "the integration ships in the `transformers` library (v4.46.0 onwards)"** — you install the library (`pip install transformers`), you don't "download the transformers"; the definite article read as the models rather than the library. Version verified: the blog announces SynthID Text in Transformers v4.46.0.
2. **"DeepMind have provided a guide on HuggingFace" → "DeepMind and Hugging Face provide a guide"** — the blog post is co-published (both teams are authors); "Hugging Face" is the company's styling (two words).
3. **"just follow the notes below" → "the example below walks through it:"** — "just" does little work; "notes" → it's a code example. The colon now points at ¶2's code block.
4. **"Thankfully, this is fairly easy" kept** — conversational, not a tell. Split from the list sentence with a full stop to avoid a second colon immediately after the Art. 50(2) sentence's colon.

##### Old draft
So how can we go about actually implementing a text-embedded watermark? The Act's actual text — outputs must be marked "in a machine-readable format and detectable as artificially generated or manipulated", with solutions "effective, interoperable, robust and reliable as far as this is technically feasible, taking into account... the costs of implementation and the generally acknowledged state of the art" ([Art. 50(2)](https://artificialintelligenceact.eu/article/50/)). The best model is the open-source solution produced by Google, SynthID. SynthID Text is applied at generation time as a logits processor (you need logits access to the model), which means you need to either have self-hosted weights or an API that exposes logit biasing.

### Implementation ¶2
#### Notes
##### Para 2 — the how.

HuggingFace `watermarking_config` on `generate()` accepts `SynthIDTextWatermarkingConfig` — works on any open-weight model. Apache 2.0, reference + production implementations.

##### Bullet of points to cover
- Code snippet slot (short, 5-8 lines)

#### Paragraph draft

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, SynthIDTextWatermarkingConfig

tokenizer = AutoTokenizer.from_pretrained("repo/id")
model = AutoModelForCausalLM.from_pretrained("repo/id")

watermarking_config = SynthIDTextWatermarkingConfig(
    keys=[654, 400, 836, 123, 340, 443, 597, 160, 57],  # 20-30 random ints recommended
    ngram_len=5,
)

outputs = model.generate(
    **tokenizer(["your prompt here"]),
    watermarking_config=watermarking_config,
    do_sample=True,
)
```

Two parameters are required. `keys` is a list of random integers used to compute g-function scores across the model's vocabulary; 20 to 30 unique numbers is the recommended range, balancing detectability against generation quality. `ngram_len` controls the robustness/detectability trade-off: the larger the value, the more detectable the watermark, at the cost of being more brittle to changes (five is a good default, and it needs to be at least 2).

Two differences from Kirchenbauer's scheme are worth noting. SynthID Text computes g-function scores across a list of random keys and applies them through a tournament sampling process, rather than one hash-seeded green/red split. And detection runs through a trained classifier rather than a token count: every configuration needs its own detector trained on watermarked and non-watermarked outputs (a minimum of 10,000 examples is recommended). The library ships the detector architecture and an end-to-end training example, but the training run is on you. Both the integration and DeepMind's reference implementation are Apache 2.0, so there's no licensing friction.

Installation is one line: `pip install "transformers[torch]"` (the `[torch]` extra pulls in PyTorch, which the watermarking classes require; plain `pip install transformers` installs but the config classes raise an ImportError without it). The library needs Python 3.10+ and PyTorch 2.6+.

*Drafting notes (this pass):*
1. **Snippet adapted from the official Hugging Face blog** (["Introducing SynthID Text", 23 Oct 2024](https://huggingface.co/blog/synthid-text), verified 2026-10-20): trimmed the comments and the `batch_decode` line, and replaced the blog's trailing `...` in `keys` with nine integers plus a comment (the ellipsis isn't valid Python). ~15 lines, over the 5-8 line guideline — kept close to the official snippet for copy-paste fidelity; trim the tokenizer/model init if you need it shorter.
2. **Config name verified (resolves revisit item 3):** `SynthIDTextWatermarkingConfig` with required params `keys` and `ngram_len`, passed as `watermarking_config=` to `model.generate()` — confirmed against the blog and the transformers `GenerationConfig` docs. Remaining before publishing: smoke-test the snippet.
3. **Parameter facts trace to the blog's "Configuring a watermark" section:** 20-30 unique random keys recommended ("to balance detectability against generation quality"); `ngram_len` 5 is "a good default", minimum 2, larger = more detectable but more brittle.
4. **The g-function/tournament-sampling sentence traces to the blog:** "a pseudo-random function, called a g-function" and the config "parameterizes the g-function and how it is applied in the tournament sampling process". Kept to two sentences so it doesn't re-open the mechanism section.
5. **The trained-classifier nuance is deliberate:** Mechanism ¶3 teaches detection = z-test, but SynthID Text's detection is a trained classifier (Bayesian detector class provided; "a minimum of 10k examples" recommended). Flagging it here stops the reader assuming the z-test applies to SynthID, and it sets up the compute-cost section (which already notes "SynthID's trained classifier costs more").
6. **Apache 2.0 clause** traces to the ¶2 notes ("Apache 2.0, reference + production implementations") and feeds the PII scenario's Art 25(4) point.
7. **¶1's colon → this code block:** if you'd rather ¶2 open with prose, change ¶1's ending to a full stop.
8. **Install line verified (2026-10-20, PyPI + smoke test):** the PyPI README's recommended command is `pip install "transformers[torch]"` (or `uv pip install "transformers[torch]"`); plain `pip install transformers` is valid but incomplete — smoke-tested it and the import resolves, but constructing `SynthIDTextWatermarkingConfig` raises `ImportError: requires the PyTorch library`. Hence the `[torch]` extra in the prose. Version requirements from the PyPI README: Python 3.10+, PyTorch 2.6+. NB current PyPI release is 5.20.2 — the blog's v4.46.0 is the *minimum* (where SynthID Text landed), so "v4.46.0 onwards" in ¶1 stays correct.
9. **Snippet params verified against the installed library source (5.20.2):** `SynthIDTextWatermarkingConfig.__init__` takes `ngram_len: int` and `keys: list[int]` ("a sequence of watermarking keys, one for each depth") plus optional `context_history_size`, `sampling_table_seed`, `sampling_table_size`, `skip_first_ngram_calls`, `debug_mode`. The library's own docstring example uses the exact same `keys=[654, 400, 836, 123, 340, 443, 597, 160, 57], ngram_len=5` as the blog snippet — the snippet is faithful. NB the blog's "20 to 30 unique, randomly generated numbers" recommendation is about *how many* keys for detectability/quality balance; the library docstring says one key per depth. Worth a one-line reconciliation in the final prose if we keep both claims.
10. **LLM-assisted tooling check (your question):** for a full runtime smoke test (actually generating watermarked text), the available tooling is the Python environment + terminal (pip install, run a script) and the debugger — no skill or slash command does model inference directly. The blocker for a full test here is PyTorch + a model download (~GBs), not tooling. If we want it, the path is: create a venv, `pip install "transformers[torch]"`, run the snippet against a small model (e.g. `google/gemma-2-2b` per the library's own example, or any open-weight model). Flagged as optional — the import/param verification above already covers the snippet's correctness.

### Implementation ¶3
#### Notes
##### Para 3 — what you can't do.

Can't watermark a closed API you don't control. If you wrap ChatGPT/Claude, the provider's watermark covers you — your job is not to strip it.

#### Paragraph draft

### The compute cost
#### Notes
Watermarking is a per-token bias on top of the forward pass: negligible relative to inference. Detection is a separate pass — a z-test is just counting green tokens (cheap); SynthID's trained classifier costs more, both far cheaper than generation. The real cost is operational: key management, detector availability, logging which outputs were watermarked. *(No published latency numbers — keep qualitative unless we verify the Nature supplementary.)*

#### Paragraph draft

### Security: the key is the attack surface
#### Notes
If the key leaks or is inferable, attackers spoof: Sadasivan et al. inferred green lists with ~1M queries (~$50) and composed human text that flags as watermarked. Private mode (Kirchenbauer §5): key secret, detection behind a rate-limited API — but then third parties can't verify, which cuts against transparency duties. *This tension is worth one honest sentence.*

##### Bullet of points to cover
- **Dangers of a public hash key (expanded):**
  - **Spoofing** (Sadasivan et al.): with the key, an attacker composes human-written text that hits the green list deliberately — human text flags as AI (AUROC 99.8% → 1.3% in their experiment). Reputational damage: derogatory text "watermarked" by a competitor's key
  - **Evasion becomes trivial**: knowing the green list, an attacker paraphrases *away from* green tokens deliberately — no quality loss needed, just pick red-list synonyms. The z-score collapses to baseline
  - **False accusations**: spoofed text + a public detector = anyone can be "proven" to have used AI. For the EU's human-editorial-control exemption, a public key undermines the trust the exemption relies on
  - **Multiple keys as mitigation** (Kirchenbauer §5): k > 1 keys, one chosen per generation, Bonferroni-corrected detection — brute-forcing all keys becomes expensive; lists constructed so each word is green for k/2 keys
  - **SynthID's answer**: trained classifier detector rather than a published key — the detector is a model, not a formula, so "publicly accessible tool" ≠ "public key". SB 942's tool mandate is satisfiable without publishing anything
- **Spoofing analogy (yours to finalise — "Claudish" / LLM tells):** the understandable version of spoofing is writing "Claudish" — text with the tell-tale LLM style: em-dashes, "not X but Y" constructions, "It's worth noting that" openers. Every LinkedIn user can spot it. But that's *human* detection, and the analogy needs one honest caveat: the watermark detector doesn't read style, it counts green tokens. Style tells fool humans; the green list fools the detector. So the full spoofing picture is worse than "Claudish" text: with the key, an attacker writes text with *no* style tells that still flags as AI — undetectable to humans, flagged by the detector. Sadasivan's spoofed sentences read as near-nonsense ("the first thing you do will be the best thing you do...") but hit 42.6% green tokens, z = 4.36 → flagged. Style mimicry fools people; key knowledge fools the detector
- **Clarity flag (as you said):** this analogy is about LLM *writing style*, NOT the watermark mechanism. The watermark is a statistical signal in token choice, not a fingerprint and not a style. Keep the two clearly separated: style tells = how humans guess; green-list statistics = how the detector knows. The analogy explains what spoofing *achieves* (text that looks AI-generated), never how the watermark *works*
- **Metaphor budget note:** the post already has the coin flip (para 2) and the Bible translation analogy (translation section). "Claudish" is a coinage rather than a metaphor, so it may fit the one-metaphor budget — but three signature devices in one post risks stacking. Your call whether "Claudish" earns its space here or lives in the spoofing sentence only
- **Yes — with SynthID Text you generate your own key (resolved):** the Apache 2.0 repo ships the key-generation machinery; the HuggingFace `SynthIDTextWatermarkingConfig` takes your key as a parameter (keys are per-deployment, not global). You are the key holder: you generate it, you store it, you decide who detects. Consequences: (1) your detector only recognises *your* outputs — cross-vendor detection doesn't exist; (2) key management is now your operational burden (rotation, storage, logging which key watermarked which output); (3) if you leak your key, your watermark is spoofable — same attack surface as any secret. ⚠️ VERIFY the exact config parameter name against the repo when drafting the code snippet

#### Paragraph draft

### The self-hosted PII scenario
#### Notes
Para 1 — the scenario: text-generating AI system (not necessarily Annex III high-risk — Art 50(2) applies to any text generator), open weights, PII/confidential data that can't leave your perimeter. No hosted watermarking API. In-content watermarking via SynthID Text in your own middleware is the only option that satisfies both data residency and Art 50(2).

Para 2 — metadata vs embedded: metadata alone (C2PA) is trivially strippable — copy-paste loses it (the live post's two-layers point). In-content survives. Whether metadata-only satisfies Art 50(2) is unresolved; in-content is the defensible reading.

Para 3 — the legal specifics (keep tight, link out): Art 50(2) covers "providers of AI systems, including general-purpose AI systems" — middleware builders are providers. The assistive-editing exemption: pass-through/light-edit middleware is out of scope; content-generating middleware is in. Cost-of-implementation is a named proportionality factor. Art 25(4): open-source components are carved out of the written-agreement requirement — Apache-2.0 SynthID means no obligation toward DeepMind, your integrator obligations remain.

#### Paragraph draft

## Builder Bottom Line

### Bottom line ¶1
#### Notes
SynthID Text in validation middleware. Generation-time, not post-hoc. Don't strip watermarks when manipulating output (ToS + Art 99(4)(g) — €15M/3%).

#### Paragraph draft

### Bottom line ¶2
#### Notes
The honest limits: needs length, dies to paraphrase and translation, code is a blindspot. Watermarking raises the cost of evasion; it doesn't make it impossible. (The live post already said "honestly, watermarking is not unbreakable" — echo, don't repeat.)

#### Paragraph draft

*Cross-links:* [Watermarking Rule Explained](https://leiwe.partners/insights/eu-ai-act-watermarking) (the "what" companion), post 2 (image), post 4 (audio), [main compliance guide](https://leiwe.partners/insights/eu-ai-act-global-impact-compliance-guide).

---

## Metaphor inventory (decide before finalising)

*Style guide rule: one metaphor per post, chosen by the writer. Current candidates:*

1. **The biassed coin** (para 2, mechanism) — *currently in the draft*. Explains the core mechanism (fair coin vs weighted coin = human vs watermarked statistics). Strongest candidate: it's load-bearing (the z-score literally measures deviation from the fair-coin expectation), it recurs in para 3 ("the fair coin from the last paragraph"), and it's the plan's own suggested device.
2. **The Bible translation analogy** (translation section) — Masoretic vs Septuagint. Explains the attacker's quality risk. Vivid for readers who know the reference, but scoped to the OT and "textual traditions" — the most niche of the three.
3. **"Claudish" / LLM tells** (spoofing) — a coinage rather than a metaphor. Most relatable for a LinkedIn audience; explains what spoofing *achieves*. Needs the style-vs-statistics caveat to work.

*My take: the coin is the winner — it's the only one that explains the mechanism itself, and the z-score callback depends on it. The Bible analogy and "Claudish" are both cuttable without losing the argument. If you keep two, keep coin + Claudish (both serve the mechanism/spoofing arc) and drop the Bible analogy to a footnote. Decide when the full draft is assembled — no need to lock it now.*

---

## Revisit list (before publishing)

1. **Mechanism section's "differentiate your output from competitors"** — marketing claim, not in the original brief; may belong in the Builder Bottom Line instead. Re-visit when the full post is assembled
2. **Metaphor inventory** — lock the winner (coin / Bible analogy / "Claudish") once the full draft exists
3. **SynthID config parameter name** — ✅ verified 2026-10-20 against the official Hugging Face blog, the transformers docs, and the installed library source (5.20.2): `SynthIDTextWatermarkingConfig` with required params `ngram_len` and `keys` (list of ints, one per depth; blog recommends 20-30 unique random numbers), passed as `watermarking_config=` to `model.generate()`. Install command verified: `pip install "transformers[torch]"` (plain install lacks PyTorch → ImportError on config construction; smoke-tested). Remaining: optional full runtime smoke test (needs PyTorch + a model download)
4. **SynthID compute overhead** — keep qualitative unless the Nature supplementary yields numbers
5. **OpenAI watermarking status** — site unfetchable (403); verify via secondary reporting before drafting the providers section
6. **"No research on watermarking AI-generated code"** (Code ¶1) — verify before publishing; software watermarking is an established field and LLM-code watermarking may exist. Safer phrasing: "I'm not aware of research testing this"
7. **Business Insider quotes — revisit when the full post is assembled** — the verified quotes from ["Claude users are canceling their subscriptions, citing Anthropic's new AI watermark"](https://www.businessinsider.com/claude-users-cancel-subscriptions-citing-anthropic-new-ai-watermark-2026-8) (Thibault Spirlet, 15 Aug 2026; full notes in [bi-claude-watermark-article-notes.md](posts/plans/post3/bi-claude-watermark-article-notes.md)) were dropped from Code ¶2 (the Rajtmajer quote argues against that paragraph's claim — see Code ¶2 note 8). Candidates for later placement once the whole article exists: **Rajtmajer** (code shipped to clients, authorship/contract penalties) → intro hook or Builder Bottom Line; **Bogosavljević** (professionally shipped code, invisible marker) → Builder Bottom Line; **Echols** ("Even if you edit your own work that you wrote, they add the watermark anyway") → paraphrase section's light-edit survival point; **Rivera Martínez** (provider lock-in) → Builder Bottom Line. Also from the article: Anthropic's watermark went live 2 Aug 2026 with the EU AI Act as the compliance driver, and OpenAI uses SynthID for supported images/audio (partially answers revisit item 5). Citation caution: the article is subscriber-only; the Rajtmajer passage is reported speech — quote as "told Business Insider", not a direct quotation.

---

## Editing workflow

1. You write paragraphs into this file (or a draft file) under each heading
2. I edit against the style guide: UK English, contractions, no em-dash defaults, no LLM tells, concrete evidence, honest uncertainty
3. Metaphor slots: you author, I flag where one would strengthen but never supply the final line
4. Claims check: every number in the prose must trace to the Sources section in post3-plan.md
