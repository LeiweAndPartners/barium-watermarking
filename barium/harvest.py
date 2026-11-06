"""Harvest candidate next-token probabilities from a served model's response.

Role: turn the OpenAI-compatible logprobs response shape into the
(token, probability) lists the demo embedder takes, so the journey from a
served model to watermarked text is one function call.

Honesty framing: barium never talks to the API itself. This module parses an
already-received response dict - the caller owns the request, the endpoint,
and the openai (or httpx) client. The helper exists because the response
shape is fiddly (choices[0].logprobs.content[i].top_logprobs[j]) and because
the units are a silent-failure trap: the API returns log-probabilities, and
passing them to embed() without exp() runs fine and produces garbage.
"""

from __future__ import annotations

import math


def harvest_top_logprobs(
    response: dict[str, object],
) -> list[list[tuple[str, float]]]:
    """Extract candidate (token, probability) pairs from a chat-completions
    response with logprobs enabled.

    Accepts the parsed JSON body of an OpenAI-compatible chat completion
    requested with ``logprobs=True, top_logprobs=N`` - the dict returned by
    ``response.model_dump()`` (openai client) or ``response.json()``
    (httpx/requests). Each generated position's top-N candidates become one
    list of (token, probability) pairs, exactly the shape
    ``DemoEmbedder.embed`` takes.

    Log-probabilities are converted with exp(): the API returns natural-log
    probabilities, and the embedder compares probabilities. Tokens are raw
    model tokens (" time", "time,"); the embedder normalises them through its
    tokenisation before any green check, so no cleaning is needed here.

    Args:
        response: Parsed chat-completions response body with logprobs.

    Returns:
        One list of (token, probability) pairs per generated position.

    Raises:
        KeyError: If the response lacks the logprobs payload - typically a
            response requested without ``logprobs=True``, or an error body.
    """
    choices = response["choices"]
    first = choices[0]
    logprobs = first["logprobs"]
    content = logprobs["content"]
    return [
        [
            (entry["token"], math.exp(entry["logprob"]))
            for entry in position["top_logprobs"]
        ]
        for position in content
    ]
