# Source Notes: Business Insider — Claude Watermark Backlash Article

*Working notes for post 3, Code ¶2 quote slot. Compiled from the article's publicly accessible content (the full article is subscriber-only; this captures what's verifiable without a subscription).*

---

## Article details

- **Title:** "Claude users are canceling their subscriptions, citing Anthropic's new AI watermark"
- **Author:** Thibault Spirlet (BI tech reporter, London — covers AI's impact on work)
- **Published:** 15 Aug 2026, 2:48 AM GMT+8
- **URL:** https://www.businessinsider.com/claude-users-cancel-subscriptions-citing-anthropic-new-ai-watermark-2026-8
- **Access:** subscriber-only, but the article's lead sections are publicly readable and the quotes below are verbatim from the accessible content. Secondary coverage (hotpaths.com, roboaidigest.com, weeklysilicon.com) quotes the same passages.

---

## The quotes (verbatim, from the accessible content)

### Vladislav Rajtmajer — freelance developer, Czech Republic
> "He said he uses AI for code reviews and translations, and worried an AI label on code shipped to clients could raise questions about authorship or trigger contract penalties."
>
> "He added that the watermark was a 'signal to look at Chinese AI providers and learn to work with other models.'"

- Canceled his Claude Max subscription on Tuesday, citing the watermark as the main reason.
- **This is the Code ¶2 quote** — code shipped to clients, authorship questions, contract penalties. Exactly the paragraph's point.

### Stevan Bogosavljević — senior software engineer, Montenegro
> "Having code attributed to Claude 'definitely would be not desirable,' he said, as he would not want professionally shipped code to carry an invisible marker that could raise questions about authorship, compliance, or client policies."

- Canceled in July (before the watermark announcement), citing service quality — but said the watermark "further validated his decision to cancel."
- Second-best quote for Code ¶2: "professionally shipped code... invisible marker... authorship, compliance, or client policies."

### Richard Echols — AI consultant, Georgia
> "Even if you edit your own work that you wrote, they add the watermark anyway," Echols said.

- Uses Claude to create documentation for businesses; worried the mark could appear when he'd written the underlying material himself and used Claude only for edits.
- **This is the Mechanism ¶2 / two-layers quote** — the mark survives light editing, which is the paraphrase section's "sloppy paraphrase doesn't save you" point in practitioner terms.

### Arturo Villarroya — public policy
- Canceled Wednesday after becoming "uncomfortable" with the watermarking plan.
- Worried a watermark could remain even when the underlying writing was original and Claude was used only to translate, check spelling, fix academic citations, or lightly summarize.
- Presence could create problems in academic and professional settings with strict AI-use rules.
- Switching to Cursor and Grok 4.6 for coding.

### Santiago Alessandro Rivera Martínez — software engineer, founder of Directa
> "When your workflow is built entirely around proprietary software, the provider can change the rules, features, restrictions, or conditions around that workflow later."
>
> "I would rather have the AI layer of my work be portable and provider-agnostic."

- The vendor-lock-in angle — useful for the Builder Bottom Line if needed.

---

## Anthropic's position (from the article)

- Watermark applied globally to text from new Claude models **from 2 August 2026**; support for older models still rolling out.
- Anthropic's blog (support.claude.com/en/articles/16266773-how-claude-marks-ai-generated-content): a detected watermark indicates Claude **processed** text, not that it was necessarily the original author. Marks can remain after Claude proofreads, translates, summarizes, or otherwise edits content.
- Watermarking "does not change the meaning, quality, or readability of Claude's response."
- **Compliance driver:** "Anthropic said that it added the watermark in order to comply with the European Union's AI Act" — useful context for the intro's hook (the PO's "make reasonable efforts" shrug).
- Plans a **free detection API** so users and third parties can check text for Claude's watermark themselves.
- Anthropic told BI it hasn't seen a trend of uptick in cancellations since announcing the watermark.
- Anthropic had 300,000 business customers as of September 2025.

---

## Other context in the article

- Dozens of people posted on X since Monday that they'd canceled, citing the watermark.
- Google uses SynthID for AI-generated content; OpenAI uses SynthID for supported images and audio (per an OpenAI X post — NB this partially answers the revisit-list item on OpenAI watermarking status, for images/audio at least).
- X adds a "Made with AI" tag on content it determines to be AI-generated or manipulated (appeared on Karoline Leavitt's resignation post, later disappeared).
- Aadit Sheth (The Narrative Company) made the transparency case: audiences should be able to tell whether words reflect a person's own thinking.

---

## Relevance check for post 3

| Quote | Post 3 home | Verdict |
|---|---|---|
| Rajtmajer (code shipped to clients, authorship/contract penalties) | Code ¶2 | **Relevant — cite it** |
| Bogosavljević (professionally shipped code, invisible marker) | Code ¶2 (alternative) | Relevant — pick one of the two |
| Echols ("they add the watermark anyway") | Mechanism ¶2 or Paraphrase section | Relevant — the light-edit survival point |
| Rivera Martínez (provider lock-in) | Builder Bottom Line | Optional |
| Anthropic's EU AI Act compliance statement | Intro hook context | Useful background, not a quote |

**Citation caution:** the article is subscriber-only. The quotes are verbatim from the publicly accessible lead sections and are corroborated by secondary coverage, but if citing in the post, link the article and quote the paraphrase ("told Business Insider") rather than implying full-text access. The Rajtmajer passage is reported speech ("He said he... worried...") — quote it as reported speech, not a direct quotation.
