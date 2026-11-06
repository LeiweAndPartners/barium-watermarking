"""Tests for the harvest helper: response-shape parsing and unit conversion."""

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from barium.harvest import harvest_top_logprobs  # noqa: E402


def _response_body() -> dict[str, object]:
    """A minimal chat-completions body with the logprobs payload.

    Mirrors the shape verified live against vLLM (top_logprobs=20): nested at
    choices[0].logprobs.content[i].top_logprobs, each entry carrying token
    and natural-log probability. Tokens are decorated the way real model
    tokens arrive.
    """
    return {
        "choices": [
            {
                "logprobs": {
                    "content": [
                        {
                            "token": " time",
                            "logprob": math.log(0.5),
                            "top_logprobs": [
                                {"token": " time", "logprob": math.log(0.5)},
                                {"token": "day", "logprob": math.log(0.3)},
                                {"token": "year", "logprob": math.log(0.2)},
                            ],
                        },
                        {
                            "token": " to",
                            "logprob": math.log(0.9),
                            "top_logprobs": [
                                {"token": " to", "logprob": math.log(0.9)},
                                {"token": "and", "logprob": math.log(0.1)},
                            ],
                        },
                    ]
                }
            }
        ]
    }


def test_harvest_returns_embedder_shape() -> None:
    """The helper returns one (token, probability) list per position."""
    candidates = harvest_top_logprobs(_response_body())
    assert len(candidates) == 2
    assert candidates[0] == [(" time", 0.5), ("day", pytest.approx(0.3)), ("year", pytest.approx(0.2))]
    assert candidates[1] == [(" to", 0.9), ("and", pytest.approx(0.1))]


def test_harvest_converts_log_probabilities() -> None:
    """The units are probabilities, not log-probabilities.

    Passing log-probabilities to embed() without exp() runs fine and produces
    garbage: the delta boost dominates any negative log-probability, so every
    position would pick the same token. This test pins the conversion.
    """
    candidates = harvest_top_logprobs(_response_body())
    for position in candidates:
        for _, probability in position:
            assert 0.0 < probability <= 1.0


def test_harvest_output_feeds_embed_round_trip() -> None:
    """The harvested shape is exactly what DemoEmbedder.embed takes."""
    from barium.detector import GreenListDetector
    from barium.embedder import DemoEmbedder

    candidates = harvest_top_logprobs(_response_body())
    detector = GreenListDetector(123456789)
    text = DemoEmbedder(detector).embed(candidates)
    assert detector.detect(text).verdict in {"watermarked", "not_watermarked", "inconclusive"}


def test_harvest_raises_on_missing_logprobs() -> None:
    """A response without the logprobs payload raises KeyError, not silence.

    The typical cause is a request without logprobs=True, or an error body:
    the caller needs the failure at the parse, not downstream at the embed.
    """
    with pytest.raises(KeyError):
        harvest_top_logprobs({"choices": [{"message": {"role": "assistant", "content": "hi"}}]})
