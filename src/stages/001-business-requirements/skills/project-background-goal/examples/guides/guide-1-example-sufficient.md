# Example 1 · Sufficient-Mode Run (Generic Scenario)

> Reference candidate artifact demonstrating a full successful run in **Sufficient mode**.
> Input was a desensitized email + meeting transcript + business-supplementary slide. Status: `ready_for_human_review`.
> Use as a comparison anchor when reviewing your own candidates.

## Input

- **SRC-001 · Meeting transcript** — 2026-08-08 product team weekly review
- **SRC-002 · Email from business owner** — "Re: 2026 春季电商大促活动 PRD 需求"
- **SRC-003 · Slide deck** — "客群分级与权益" (desensitized)

## Run Trace

| Step | Time | Outcome |
|---|---|---|
| Preflight | T+00:00 | Input sufficiency = **sufficient mode** (3 sources, ≥ 50 chars) |
| Intake | T+00:01 | 3 SRCs registered; role separation: business fact owner = VP of CRM, goal decision owner = VP of Marketing |
| Think (7 lenses) | T+00:02 | First Principles isolated "VVIP invitation routing" as the real problem; Adversarial surfaced a conflict between SRC-002 and SRC-003 on VVIP definition |
| Clarify Session 1 | T+00:03 | Q: "VVIP threshold?" → Answer: ¥NNNk/year (NNN-NNN% of customer base) |
| Clarify Session 2 | T+00:05 | Q: "Fulfillment error rate baseline?" → Answer: NNN% (verified from CRM 2025 data) |
| Clarify Session 3 | T+00:07 | Q: "Post-event follow-up owner?" → Answer: VP of CRM (after PM escalates) |
| Draft v0.1 | T+00:09 | All 14 sections filled; **no 待确认 left unfilled** (all answered via Sessions) |
| Self-Audit | T+00:10 | `validate_artifact.py` returns `{"ok": true, "warnings": 1}` (semantic warning on placeholder count is expected and within limits) |
| Human Gate | T+00:11 | Status flips to `ready_for_human_review` |

## Why This Is A Good Example

1. **3 sources used at full strength** — the artifact cites SRC-001/002/003 multiple times across sections, never padding content from a single source.
2. **All 6 knowledge-state labels appear** — `FACT` (with SRC), `DECISION`, `ASSUMPTION`, `AI_INFERENCE`, `UNKNOWN`, `CONFLICT` (resolved in §10).
3. **Every §11 question has a corresponding Clarifications Session row** — no orphan questions.
4. **Constitution Compliance has at least 1 JUSTIFIED row** — shows the team can declare tradeoffs, not just rubber-stamp.
5. **Numbers all have a baseline + a target + a measure + a time horizon** — no "improve UX" style goals.
6. **No `待确认` markers outside §10/§11/§Clarifications** — body sections are concrete.

## Common Traps To Watch

- ❌ **Padding from one source only** — if §1–§7 cite SRC-001 nine times and SRC-002 once, you have one source, not three.
- ❌ **Goals without time horizon** — "提升复购率" without "12 个月" is a wish, not a goal.
- ❌ **Hidden assumptions** — anything that looks like `FACT` but has no `SRC-*` in the same row is an `AI_INFERENCE` you forgot to relabel.
- ❌ **§11 without §Clarifications** — open questions without logged sessions means you never asked the human.

## Cross-Reference

- See `references/question-patterns.md` for the 8 canonical question templates.
- See `references/audit-checklist.md` for the 5 gates this example satisfies.
- See `references/output-contract.md` § Clarifications Session Contract for the row schema used in the example artifact.
