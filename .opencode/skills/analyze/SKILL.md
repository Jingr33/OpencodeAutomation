---
name: analyze
description: Converts runtime logs and errors into numbered, structured local issue analyses
license: MIT
compatibility: opencode
---

1. Parse only the errors present in the supplied logs.
2. Read the relevant source files in the active repository.
3. Create `issues/<NNN>-<slug>/issue.md` from
   `.opencode/templates/issue-analysis.md`.
4. Never reuse an existing number. If re-analyzing an issue with `fix.md`, rename
   it to `fix-obsolete.md` first.
5. Include concrete file paths, line numbers, root cause, and possible fixes.
