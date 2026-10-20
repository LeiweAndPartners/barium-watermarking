# Code Standards: the anti-slop contract

*Binding for every Builder hand-off and every Reviewer checklist. The goal: a human can read the repository top to bottom and understand every line, diagram, and page without guessing. These plan documents follow the same rules.*

## Comments

- Comments explain **why**, never what. If a competent reader can infer the comment from the line below it, delete the comment.
- Every non-obvious algorithm section cites its source: arXiv:2301.10226 §2, or the specific file in `jwkirchenbauer/lm-watermarking`.
- UK English throughout: summarise, penalise, labelled, organisation, recognise.
- No emoji anywhere: code, docs, commit messages, CLI output.
- No filler openers: "Note that", "It's worth noting", "Simply", "Obviously".
- Docstrings: one-line summary first; parameters, returns, and raises where non-trivial. Module docstrings state the module's role, and its honesty framing where relevant (the embedder is a labelled demo, not production generation).

## Mermaid

Silent parse failures in VS Code Markdown preview come from a few known causes, so the safe form is mandatory:

- Quote every label: `A["..."]`, `D{"..."}`
- Line breaks inside quoted labels use `<br/>`, never `\n`
- No raw `&`; write "and"
- Verify a new diagram in Markdown preview before signing off a docs hand-off

Planned diagrams: system architecture, detection dataflow, MCP sequence, key lifecycle.

## HTML guides

- Location: `docs/guides/*.html`, one concept per page.
- Self-contained: no CDN, no external fonts, no build step; every page runs from `file://` with no network access. The local-first ethos extends to the docs.
- Vanilla JS only; no frameworks, no transpilation.
- Each page carries a worked example with real numbers, and links back to the README and the paper.
- Planned guides: green-list derivation, the z-test with a worked example, key management, the MCP protocol walkthrough.

## Python

- Floor: Python 3.10. Runtime dependencies: none (stdlib only). Dev dependency: pytest.
- Type hints on all public functions; dataclasses for result types.
- `secrets` for all key material, never `random`.
- No hardcoded keys anywhere; keygen refuses known defaults.
- Naming: modules lowercase, classes CapWords, constants UPPER_SNAKE.

## Commits

- Imperative mood, one line, no emoji, reference the phase: `phase 3: green-list detector with hand-computed z-score tests`.
