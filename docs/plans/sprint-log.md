# Sprint Log

*Appended by the Scrum Master after every gate: date, phase, gate, verdict, notes. One line per entry where possible.*

| Date | Phase | Gate | Verdict | Notes |
|---|---|---|---|---|
| 2026-10-20 | 1 Plan lock | n/a | complete | Plan documents written; roster (PM, Builder, Reviewer, Scrum Master), two gates per phase, Python 3.10 floor, and build-through-push scope agreed with Marcus |
| 2026-10-20 | plan amendment | n/a | complete | Four-quadrant test matrix (TP/TN/FP-rate/FN) added to Phases 3-4; new Phase 5 Calibration for minimum detectable length (`experiments/min_tokens.py` + `docs/min-tokens.md`); phases renumbered to 8 |
| 2026-10-20 | 2 Skeleton | test gate | green | `pip install -e .` succeeds; `barium --help` and `barium-mcp --help` exit 0; pytest 6 passed. One process correction logged: the gate was initially run before the Builder hand-off (looping on a missing pyproject.toml); re-run once with files in place |
| 2026-10-20 | 2 Skeleton | review gate | request changes | Reviewer: positioning rule in `barium/cli.py` help must be verbatim with em dash; `tests/test_cli.py` must pin the full rule sentence. Builder applied both fixes; suite re-run green (6 passed) |
| 2026-10-20 | 2 Skeleton | review gate | approved | Re-review confirmed em dash (U+2014) in help description and full-sentence assertion in test. PM sign-off next; commit and advance to Phase 3 |
