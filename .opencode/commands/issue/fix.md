---
description: Implement a fix from a numbered local issue analysis
subtask: true
---

Given an issue number, find `issues/<NNN>-*/issue.md`. Read it as a read-only
specification, inspect referenced source files, implement the fix using the
active repository's conventions, and create `fix.md` from
`.opencode/templates/fix.md`. Do not modify `issue.md`, run Git operations, or
push changes. Update documentation only when behavior or architecture changes.
