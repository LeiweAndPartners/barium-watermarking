# Threat Model

*The key is the attack surface. Extracted from arXiv:2301.10226 §5 and §7 and Sadasivan et al. (arXiv:2303.11156); every number traces to `docs/plans/post3-plan.md` or `docs/min-tokens.md`.*

## The key is the attack surface

Everything in the scheme hangs off the key: the same key derives the green lists at generation and re-derives them at detection. If the key leaks, an attacker can do two things — spoof and evade. If the key is *inferable*, the same two things are possible without ever seeing it.

Barium's key space is $2^{31} \approx 2.1 \times 10^9$ values, drawn from `secrets`. That is large enough that accidental collision between deployments is negligible and small enough that keys stay readable in configuration — but it is not a cryptographic barrier against a determined attacker who can query a watermarked system, because the attack below does not need to brute-force the key.

## Spoofing

Sadasivan et al. (arXiv:2303.11156, TMLR) demonstrate the spoofing attack: an attacker who can query a watermarked model roughly **1 million times** can infer the green lists and then compose purely human text that flags as watermarked. Their measured result: AUROC against the watermarked model drops from 99.8% to 1.3% once the green lists are inferred — the detector's verdict becomes attacker-controlled.

The defence is operational, not mathematical: keep the key secret, and rate-limit access to any watermarked generation endpoint. A per-deployment key (barium's model) limits the blast radius of a leak to one deployment.

## Evasion

Paraphrase is the natural evasion: moving tokens away from the green lists their predecessors induce destroys the signal. Sadasivan et al.'s recursive paraphrasing drops watermark TPR@1%FPR from **99.3% to 9.7%** on 300-token passages, with two rounds sufficient to fall below 50%. Kirchenbauer et al. estimate removal "requires modifying roughly one quarter of the tokens or more".

The quality trade-off cuts both ways: 77% of the paraphrases in the Sadasivan study preserved content at high quality, so a capable paraphraser evades at near-zero meaning cost — while smaller paraphrasers degrade quality more. Translation is the same attack across languages: He et al. 2024 (ACL 2024) show current watermarks "lack consistency" under translation, with their cross-lingual removal attack dropping AUC to random-guessing level.

Barium's own measured evasion point: 75% token substitution drops the demo watermark's z below threshold, while 50% does not — partial paraphrase can be sufficient to trigger detection, which is the paper's point, not a weakness of this implementation.

## Private mode and its trade-off

Kirchenbauer §5 distinguishes two operating modes:

- **Public mode**: the key (or the detector) is public. Anyone can verify — but anyone can also spoof, because the green lists are derivable.
- **Private mode**: the key stays secret and detection runs behind a rate-limited API. Spoofing becomes much harder — but third parties can no longer verify, which cuts against transparency duties.

Barium is built for the first pattern with the second available: the key is per-deployment secret material, and nothing in the package requires publishing it. The trade-off is yours to make, and it is a real one — verifiability and spoof-resistance pull in opposite directions.

## Multiple keys with Bonferroni correction

One mitigation for key inference: run $k$ independent watermarks with $k$ keys and detect with any of them. Each detector's false-positive rate multiplies under naive combination, so the per-detector threshold is corrected with Bonferroni: to keep the family-wise false-positive rate at $\alpha$, test each key at $\alpha / k$.

For $k = 4$ keys and a family-wise FPR of $3 \times 10^{-5}$, each detector runs at $\alpha/k = 7.5 \times 10^{-6}$, which corresponds to $z \approx 4.33$ instead of $z = 4$: $4 \times Q(4.33) \approx 3 \times 10^{-5}$. The cost is length: the minimum detectable length grows with the threshold, so multiple keys buy spoofing resistance at the price of longer text. The z-score remains a false-positive rate under the correction — the family-wise rate is what you control, not a certainty.

## What the threat model does not cover

- **SynthID Text.** Barium detects the open green-list scheme only; SynthID's detector is a trained classifier tied to a private config, and its threat model is the provider's, not this package's.
- **Arbitrary AI-text detection.** No statistical watermark detector identifies "AI text" in general; barium identifies one scheme's mark.
- **Metadata stripping.** C2PA-style provenance in metadata is trivially strippable by copy-paste; in-content watermarking survives it. That is post 1 of the series' two-layers point, not this package's scope.
