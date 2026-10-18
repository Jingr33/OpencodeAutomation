# Structured Reporting

Every summary or report that a human or another agent may read MUST use a
structured format: fixed headings, one fact per point, and an explicit status
for each stage. This applies to Issue comments, pull-request bodies, support
summaries, review-fix notes, and final replies.

## Canonical summary structure

Use these headings in order. Omit a heading only when it has no content.

1. `# <task or artifact> — Summary` — one short title.
2. `## Status` — one line: `succeeded`, `partial`, `blocked`, `failed`,
   `planned`, or `unchanged`, followed by the single most important outcome.
   These status words are defined in
   [output-format.md](../contracts/output-format.md).
3. `## Context` — repository, branch, Issue or PR, and workspace as points.
4. `## Stages` — a table with one row per work stage in execution order:

   | Stage | Status | Notes |
   | --- | --- | --- |
   | inspect | done | ... |
   | implement | done | ... |
   | verify | done | ... |

   Status is `done`, `skipped`, `blocked`, or `failed`. Notes state the
   result, not the activity. A skipped or blocked stage MUST keep its reason.
5. `## Changes` — one bullet per changed file or behavior:
   ``- `path/to/file` — what changed and why``.
6. `## Verification` — a table with one row per check:
   `| Check | Command | Result |`. Record the exact command and its result.
7. `## Follow-ups` — outstanding work, skipped checks, and next actions;
   write `- none` when nothing remains.

Templates in `.opencode/templates/` define their own section names; their
content MUST still follow the writing rules below and use points or tables
instead of prose.

## Writing rules

- One fact per point. Do not merge unrelated facts into one bullet.
- No prose paragraphs. A fact is a bullet, a table row, or a numbered step.
- Keep stage names stable across reports so reports can be compared.
- Reference files as `` `path/to/file` `` and commands as `` `command` ``.
- Never omit skipped, blocked, or failed work; state the reason.
- Keep the report short and link to evidence instead of pasting long output.
- A final reply to the user uses the same structure as the written summary.
