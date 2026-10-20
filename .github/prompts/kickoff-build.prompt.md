---
description: Kick off the barium-watermarking agentic build per docs/plans/build-plan.md, starting at Phase 2
---

Run the barium-watermarking build per docs/plans/build-plan.md. Work autonomously through the phases.

Read first, in this order:
1. docs/plans/build-plan.md — phases, gates, acceptance criteria
2. docs/plans/agent-briefs.md — role briefs; you are the Scrum Master
3. docs/plans/code-standards.md — the quality contract for every hand-off
4. docs/plans/sprint-log.md — Phase 1 is complete; start at Phase 2

Operating rules:
- The plan is locked. Do not re-plan or renegotiate scope. If the plan and the README conflict, the README's honesty framing wins.
- You are the Scrum Master: todo list, both gates, sprint log, all git operations.
- Write each phase brief (PM duties) before starting the phase.
- Implement via Builder passes: one deliverable per brief, tests in the same hand-off.
- Every diff gets a separate Reviewer pass — launch a subagent with the Reviewer brief from agent-briefs.md, listing the changed files and the phase's acceptance criteria. Never write and approve in the same context.
- Test gate: .venv/bin/python -m pytest (venv exists: Python 3.14.3, pytest 9.1.1). A red suite goes straight back to the Builder.
- Append a line to docs/plans/sprint-log.md after every gate.

Hard stops:
- Honesty-framing wording is never guessed: green-list scheme only, the z-score is a false-positive rate, the ~25-token caveat. If a sentence could imply SynthID detection or overstate certainty, stop that item and log it.
- Three failed attempts on the same problem: log the blocker in the sprint log and stop that deliverable.
- Never advance a phase with a red suite or an open review item.

Phase 3 begins with docs/plans/algorithm-spec.md, extracted from arXiv:2301.10226 §2 and jwkirchenbauer/lm-watermarking, before any detector code is written.

Phase 8 is release: tag, create the GitHub repo under LeiweAndPartners, push. Commit per phase using the format in code-standards.md.
