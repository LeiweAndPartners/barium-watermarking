# Phase 2 Brief: Skeleton

*Written by the PM before the phase starts, per `build-plan.md`. Scope: the package skeleton only. No algorithm code — that is Phase 3, and it starts with `algorithm-spec.md`.*

## Deliverables

1. `pyproject.toml` — project metadata and console scripts
2. `barium/` package — `__init__.py` plus stub modules: `detector.py`, `embedder.py`, `keygen.py`, `cli.py`, `mcp_server.py`
3. `tests/` — one test file per module
4. `LICENSE` — MIT, copyright Leiwe & Partners
5. `.gitignore` — standard Python
6. git initialised with an initial commit (Scrum Master performs the git operations)

## Files in scope

- `pyproject.toml`
- `barium/__init__.py`, `barium/detector.py`, `barium/embedder.py`, `barium/keygen.py`, `barium/cli.py`, `barium/mcp_server.py`
- `tests/test_detector.py`, `tests/test_embedder.py`, `tests/test_keygen.py`, `tests/test_cli.py`, `tests/test_mcp_server.py`
- `LICENSE`, `.gitignore`

## Acceptance criteria (binary)

- [ ] `pyproject.toml`: name `barium-watermarking`, `requires-python >= 3.10`, `dependencies = []` (zero runtime dependencies), console scripts `barium = barium.cli:main` and `barium-mcp = barium.mcp_server:main`, pytest as the only dev dependency
- [ ] Every stub module has a module docstring stating its role and, where relevant, its honesty framing; the CLI and MCP stubs expose a `main()` entry point so the console scripts resolve
- [ ] `barium --help` exits 0; `barium-mcp --help` exits 0
- [ ] `pip install -e .` succeeds
- [ ] pytest collects cleanly with zero failures
- [ ] `LICENSE` is the MIT text with "Leiwe & Partners" as the copyright holder
- [ ] `.gitignore` covers `__pycache__/`, `.venv/`, `dist/`, `*.egg-info/`, and pytest caches
- [ ] No production algorithm code appears in this phase (no hash construction, no green-list derivation, no z-score)

## Honesty-framing lines that apply

The CLI stub's help description must use the README's positioning rule verbatim: "A detection tool for the open green-list scheme — not a SynthID tool." No sentence in any stub may imply SynthID detection or overstate certainty. The embedder stub's docstring must label it as a reference demo, not production generation.

## Out of scope

Detector math, keygen behaviour, embedder logic, real CLI subcommands, MCP protocol handling, README prose, experiments. Each arrives in its own phase.
