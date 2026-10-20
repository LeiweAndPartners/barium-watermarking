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
        seed: int = 0,
    ) -> str:
        """Select one token per position from candidate probabilities.

        Implements the bias rule from algorithm-spec.md (The demo embedder's
        bias rule): each candidate's probability is boosted by delta when the
        token is green given the selected predecessor, and the highest
        boosted probability wins. The first position has no predecessor, so
        it is selected by probability alone.

        Args:
            candidates: Candidate next-token probabilities, one list of
                (token, probability) pairs per position.
            seed: Unused; kept for API symmetry. Selection is deterministic
                given the candidates.

        Returns:
            The watermarked text: the selected tokens joined with spaces.
        """
        tokens: list[str] = []
        for position, options in enumerate(candidates):
            if not options:
                continue
            if position == 0:
                tokens.append(max(options, key=lambda pair: pair[1])[0])
                continue
            previous = tokens[-1]
            green = self.detector.green_list(previous)
            tokens.append(
                max(options, key=lambda pair: self._boosted(pair, green))[0]
            )
        return " ".join(tokens)

    def _boosted(self, pair: tuple[str, float], green: frozenset[str]) -> float:
        """Return the boosted probability for one (token, probability) pair.

        The soft rule: green candidates are boosted by delta, red candidates
        keep their probability.
        """
        token, probability = pair
        if self.detector._token_id(token) in green:
            return probability + self.delta
        return probability


def selftest(key: int, num_tokens: int = 200, seed: int = 0) -> dict[str, object]:
    """Embed then detect in one pass: the round-trip proof.

    Builds a high-entropy candidate pool, embeds a watermarked text with the
    demo embedder, and scores it with the detector.

    Args:
        key: Per-deployment secret key.
        num_tokens: Target length of the embedded text.
        seed: Unused; kept for API symmetry. Selection is deterministic.

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


def _candidate_pool(num_tokens: int) -> list[list[tuple[str, float]]]:
    """Build a high-entropy candidate pool for the demo embed.

    Each position offers several common English words with near-uniform
    probabilities, so the embedder has real freedom to prefer green
    candidates - the high-entropy setting the paper's 25-token claim applies
    to. Probabilities are near-uniform so the delta boost, not the base
    probability, decides the selection.
    """
    words = (
        "time year people way day man thing woman life child world school "
        "state family student group country problem hand part place case "
        "week company system program question work government number night "
        "point home water room mother area money story fact month lot right "
        "study book eye job word business issue side kind head house service "
        "friend father power hour game line end member law car city community"
    ).split()
    probability = 1.0 / len(words)
    return [[(word, probability) for word in words] for _ in range(num_tokens)]
