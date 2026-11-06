"""Reference demo embedder.

Role: select tokens biased toward the green list given candidate next-token
probabilities, so the embed-then-detect round-trip is provable without torch.
The bias rule follows algorithm-spec.md (The demo embedder's bias rule) and
arXiv:2301.10226 §2 Algorithm 2: green candidates are boosted by a fixed
additive bias before selection.

Honesty framing: this is a labelled reference demo, not production generation.
It ships no language model and makes no claim to generation quality - it
biases a supplied candidate distribution toward the green list so the
round-trip can be demonstrated end to end. This is the open green-list scheme
only, not SynthID Text.
"""

from __future__ import annotations

from barium.detector import GreenListDetector, tokenize

# Additive bias applied to green candidates before selection, matching the
# reference implementation's default delta (algorithm-spec.md, The demo
# embedder's bias rule).
DEFAULT_DELTA = 2.0


class DemoEmbedder:
    """Reference demo embedder biasing token selection toward the green list.

    Given candidate next-token probabilities, green candidates are boosted by
    delta and the highest-boosted candidate is selected - the soft rule from
    arXiv:2301.10226 §2 Algorithm 2, applied over a supplied candidate
    distribution rather than model logits. The result is a watermarked text
    the detector scores above threshold at sufficient length - and a
    demonstration, not a generator.

    Args:
        detector: The GreenListDetector whose key and gamma define the split.
        delta: Additive boost applied to green candidates.
    """

    def __init__(self, detector: GreenListDetector, delta: float = DEFAULT_DELTA) -> None:
        self.detector = detector
        self.delta = delta

    def embed(
        self,
        candidates: list[list[tuple[str, float]]],
    ) -> str:
        """Select one token per position from candidate probabilities.

        Implements the bias rule from algorithm-spec.md (The demo embedder's
        bias rule): each candidate's probability is boosted by delta when the
        token is green given the selected predecessor, and the highest
        boosted probability wins. The first position has no predecessor, so
        it is selected by probability alone.

        Candidates are normalised through the detector's tokenisation before
        any green check: real model tokens arrive decorated (" time",
        "time,", "Time"), and the detector scores the normalised form, so
        checking the raw string would hash a different token than the
        detector sees and break the round-trip. When several candidates
        normalise to the same token, the highest probability wins.

        Args:
            candidates: Candidate next-token probabilities, one list of
                (token, probability) pairs per position. Tokens may be raw
                model tokens; they are normalised internally.

        Returns:
            The watermarked text: the normalised selected tokens joined with
            spaces, matching what the detector scores.
        """
        tokens: list[str] = []
        for options in candidates:
            normalised = self._normalise(options)
            if not normalised:
                continue
            if not tokens:
                # The first emitted token has no predecessor, so it is
                # selected by probability alone. Keyed on emitted tokens
                # rather than the enumerate index: an empty first candidate
                # list must not hand the green boost to the next position.
                tokens.append(max(normalised, key=lambda pair: pair[1])[0])
                continue
            previous = tokens[-1]
            green = self.detector.green_list(previous)
            tokens.append(
                max(normalised, key=lambda pair: self.boosted(pair, green))[0]
            )
        return " ".join(tokens)

    def _normalise(
        self, options: list[tuple[str, float]]
    ) -> list[tuple[str, float]]:
        """Map candidates into the detector's token space.

        Each candidate token is run through the detector's tokenisation (the
        same lowercasing, whitespace split, and punctuation strip that
        detect() applies), so green membership is checked on the form the
        detector scores. Multi-token candidates collapse to their first
        token; candidates that normalise to nothing are dropped. When
        several candidates share a normalised form, the highest probability
        is kept.
        """
        best: dict[str, float] = {}
        for token, probability in options:
            parts = tokenize(token)
            if not parts:
                continue
            key = parts[0]
            if probability > best.get(key, float("-inf")):
                best[key] = probability
        return list(best.items())

    def boosted(self, pair: tuple[str, float], green: frozenset[int]) -> float:
        """Return the boosted probability for one (token, probability) pair.

        The soft rule: green candidates are boosted by delta, red candidates
        keep their probability. Public because the boost rule is part of the
        embedder's contract, not an implementation detail: a caller building
        its own selection loop over the same candidates needs the same rule.
        """
        token, probability = pair
        if self.detector._token_id(token) in green:
            return probability + self.delta
        return probability


def selftest(key: int, num_tokens: int = 200) -> dict[str, object]:
    """Embed then detect in one pass: the round-trip proof.

    Builds a high-entropy candidate pool, embeds a watermarked text with the
    demo embedder, and scores it with the detector.

    Args:
        key: Per-deployment secret key.
        num_tokens: Target length of the embedded text.

    Returns:
        A dict with the embedded text and the DetectionResult statistics.
    """
    detector = GreenListDetector(key)
    embedder = DemoEmbedder(detector)
    candidates = _candidate_pool(num_tokens)
    text = embedder.embed(candidates)
    result = detector.detect(text)
    return {
        "text": text,
        "num_tokens": len(tokenize(text)),
        "result": result,
        "embedder": "demo",
    }


# The demo pool's word list, shared with experiments/min_tokens.py so the
# calibration and the selftest measure the same high-entropy setting.
#
# Hard-coded on purpose: a stdlib-only demo needs no configurable pool, and
# the calibration tables in docs/min-tokens.md are traced to this exact list
# (67 words). Editing it silently shifts every traced number — the
# width-sensitivity table, the p = 1.00 ceiling, the low-entropy floor —
# without breaking a single test. Regenerate the tables after any change
# here (python experiments/min_tokens.py), and say so in the changelog.
DEMO_WORDS: tuple[str, ...] = (
    "time year people way day man thing woman life child world school "
    "state family student group country problem hand part place case "
    "week company system program question work government number night "
    "point home water room mother area money story fact month lot right "
    "study book eye job word business issue side kind head house service "
    "friend father power hour game line end member law car city community"
).split()


def _candidate_pool(num_tokens: int) -> list[list[tuple[str, float]]]:
    """Build a high-entropy candidate pool for the demo embed.

    Each position offers several common English words with near-uniform
    probabilities, so the embedder has real freedom to prefer green
    candidates - the high-entropy setting the paper's 25-token claim applies
    to. Probabilities are near-uniform so the delta boost, not the base
    probability, decides the selection.
    """
    probability = 1.0 / len(DEMO_WORDS)
    return [[(word, probability) for word in DEMO_WORDS] for _ in range(num_tokens)]
