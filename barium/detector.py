"""Green-list watermark detection.

Role: re-derive the green/red vocabulary split from the key, count green
tokens in the text, and compute a one-proportion z-score against the fair-coin
expectation. The construction follows arXiv:2301.10226 §2 and the reference
implementation at ``jwkirchenbauer/lm-watermarking`` (``watermark_processor.py``);
the line-by-line spec is docs/plans/algorithm-spec.md.

Tokenisation strategy: barium ships no tokenizer and no model, so it defines
its own deterministic tokenisation - text is lowercased, split on whitespace,
and leading/trailing punctuation is stripped from each token. The same text
always produces the same token sequence and the same z-score. The consequence:
barium detects watermarks generated and detected with barium's own
tokenisation; text watermarked with a different tokenizer's token ids is out
of scope for the round-trip guarantee.

Honesty framing: the z-score is a false-positive rate, not a certainty
percentage. A threshold of z = 4 means unwatermarked text exceeds it with
probability about 3e-5 - the rate at which human text is flagged, not a
measure of how certain a flag is. This detects the open green-list scheme
only, not SynthID Text (whose detector is a trained classifier tied to a
private config). Short or low-entropy text carries no signal: the paper's
"as few as 25 tokens" claim applies to high-entropy text, and low-entropy
text caps the achievable green rate (Appendix G).
"""

from __future__ import annotations

import hashlib
import math
import random
import string
from dataclasses import dataclass

from barium.keygen import validate_key

# Verdicts are hypothesis-test outcomes at the configured threshold, not
# confidence percentages. INCONCLUSIVE covers text too short to score.
WATERMARKED = "watermarked"
NOT_WATERMARKED = "not_watermarked"
INCONCLUSIVE = "inconclusive"

# Default threshold: unwatermarked text exceeds z = 4 with probability about
# 3e-5 (the standard-normal upper tail), per arXiv:2301.10226 §2.
DEFAULT_Z_THRESHOLD = 4.0

# Below this many scored positions the verdict is inconclusive rather than a
# low-confidence flag. The paper's "as few as 25 tokens" applies to
# high-entropy text; the exact operating minimum is calibrated in Phase 5.
DEFAULT_MIN_SCORED_TOKENS = 25

# Vocabulary size for the green/red split. Barium ships no tokenizer, so the
# split is over a fixed synthetic vocabulary: large enough that the gamma
# fraction behaves like the paper's setup, small enough that permutations
# stay cheap to draw in pure Python.
VOCAB_SIZE = 50_000


@dataclass(frozen=True)
class DetectionResult:
    """Outcome of one detection pass.

    Attributes:
        num_tokens_scored: Scored positions T (tokens with a predecessor).
        num_green_tokens: Green tokens counted G.
        green_fraction: G / T.
        z_score: The one-proportion z statistic.
        p_value: Standard-normal upper tail at the z-score.
        z_threshold: The threshold the verdict was evaluated at.
        verdict: WATERMARKED, NOT_WATERMARKED, or INCONCLUSIVE.
    """

    num_tokens_scored: int
    num_green_tokens: int
    green_fraction: float
    z_score: float
    p_value: float
    z_threshold: float
    verdict: str


def tokenize(text: str) -> list[str]:
    """Tokenise text deterministically: lowercase, split on whitespace, strip
    leading and trailing punctuation.

    Args:
        text: The raw text.

    Returns:
        The token sequence. Empty tokens are dropped.
    """
    tokens = []
    for raw in text.lower().split():
        stripped = raw.strip(string.punctuation)
        if stripped:
            tokens.append(stripped)
    return tokens


class GreenListDetector:
    """One-proportion z-test detector for Kirchenbauer-style green-list watermarks.

    Re-derives the green list for each scored position from the key and the
    previous token, counts green tokens, and evaluates the z statistic
    z = (G - gamma*T) / sqrt(T*gamma*(1-gamma)) against a threshold. Pure
    stdlib; no model access.

    Args:
        key: Per-deployment secret key (see barium.keygen).
        gamma: Green-list fraction of the vocabulary (paper default 0.5).
        z_threshold: Verdict threshold (default 4.0, false-positive rate
            about 3e-5).
        min_scored_tokens: Scored positions below which the verdict is
            inconclusive.
        vocab_size: Size of the synthetic vocabulary the split is drawn over.
    """

    def __init__(
        self,
        key: int,
        gamma: float = 0.5,
        z_threshold: float = DEFAULT_Z_THRESHOLD,
        min_scored_tokens: int = DEFAULT_MIN_SCORED_TOKENS,
        vocab_size: int = VOCAB_SIZE,
    ) -> None:
        self.key = validate_key(key)
        if not 0.0 < gamma < 1.0:
            raise ValueError("gamma must be in (0, 1)")
        self.gamma = gamma
        self.z_threshold = z_threshold
        self.min_scored_tokens = min_scored_tokens
        self.vocab_size = vocab_size
        # Drawing a full vocab permutation per position is the detector's
        # dominant cost; the reference implementation caches its expensive
        # re-seeding for the same reason (_get_ngram_score_cached with
        # lru_cache). Keyed on (key, gamma, vocab_size, previous_token) so a
        # changed parameter never reuses a stale split.
        self._green_cache: dict[tuple[int, float, int, str], frozenset[str]] = {}

    def _token_id(self, token: str) -> int:
        """Map a token deterministically into the synthetic vocab space.

        The green/red split is drawn over vocab ids (integers in
        [0, vocab_size)), so each token needs a stable id in that space.
        blake2b rather than ``hash()``: built-in string hashing is randomised
        per process, which would make the split process-dependent and break
        reproducibility across runs and machines.
        """
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        return int.from_bytes(digest, "big") % self.vocab_size

    def green_list(self, previous_token: str) -> frozenset[str]:
        """Return the green list induced by the previous token.

        Seed construction follows the reference implementation's ``simple_1``
        scheme: the seed is the hash key times the previous token id
        (algorithm-spec.md, Seed derivation). The hash key is the user's key;
        the token id is the sum of the UTF-8 code points of the token, a
        deterministic stand-in for a tokenizer id. The green list is the first
        floor(gamma * vocab_size) entries of the seeded permutation
        (algorithm-spec.md, Green-list size).

        Args:
            previous_token: The token immediately before the position scored.

        Returns:
            The green vocabulary for positions following previous_token.
        """
        cache_key = (self.key, self.gamma, self.vocab_size, previous_token)
        cached = self._green_cache.get(cache_key)
        if cached is not None:
            return cached
        previous_id = sum(previous_token.encode("utf-8"))
        seed = self.key * previous_id
        rng = random.Random(seed)
        green_size = int(self.vocab_size * self.gamma)
        permutation = rng.sample(range(self.vocab_size), self.vocab_size)
        green = frozenset(permutation[:green_size])
        self._green_cache[cache_key] = green
        return green

    def is_green(self, previous_token: str, token: str) -> bool:
        """Return whether token is green given the previous token.

        Args:
            previous_token: The token immediately before token.
            token: The token being scored.

        Returns:
            True when token is in the green list for this position.
        """
        return self._token_id(token) in self.green_list(previous_token)

    def detect(self, text: str) -> DetectionResult:
        """Score text and return the hypothesis-test outcome.

        Tokens are scored from the second onward: each token is checked
        against the green list derived from its predecessor. The z statistic
        follows algorithm-spec.md, The z formula; the p-value is the
        standard-normal upper tail computed with math.erfc (the same quantity
        scipy.stats.norm.sf computes in the reference implementation).

        Args:
            text: The raw text to score.

        Returns:
            A DetectionResult. The verdict is INCONCLUSIVE when fewer than
            min_scored_tokens positions are available.
        """
        tokens = tokenize(text)
        num_scored = max(len(tokens) - 1, 0)
        if num_scored < self.min_scored_tokens:
            return DetectionResult(
                num_tokens_scored=num_scored,
                num_green_tokens=0,
                green_fraction=0.0,
                z_score=0.0,
                p_value=0.5,
                z_threshold=self.z_threshold,
                verdict=INCONCLUSIVE,
            )

        green_count = 0
        for previous, current in zip(tokens, tokens[1:]):
            if self._token_id(current) in self.green_list(previous):
                green_count += 1

        z = self._z_score(green_count, num_scored)
        p = math.erfc(z / math.sqrt(2.0)) / 2.0
        verdict = WATERMARKED if z > self.z_threshold else NOT_WATERMARKED
        return DetectionResult(
            num_tokens_scored=num_scored,
            num_green_tokens=green_count,
            green_fraction=green_count / num_scored,
            z_score=z,
            p_value=p,
            z_threshold=self.z_threshold,
            verdict=verdict,
        )

    def _z_score(self, green_count: int, num_scored: int) -> float:
        """Compute the one-proportion z statistic.

        Follows the reference implementation's ``_compute_z_score``:
        numer = G - gamma*T, denom = sqrt(T*gamma*(1-gamma)).
        """
        numer = green_count - self.gamma * num_scored
        denom = math.sqrt(num_scored * self.gamma * (1.0 - self.gamma))
        return numer / denom
