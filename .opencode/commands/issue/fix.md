---
description: Implement a fix from a GitHub Issue (e.g. /issue.fix 42)
subtask: true
---

Load `github-issues`. The first argument is a required GitHub Issue number.
Fetch the complete Issue body with `gh issue view`. Read it as a read-only
specification, inspect referenced source files, implement the fix using the
active repository's conventions, and write a fix summary using
`.opencode/templates/fix.md`. Post the summary as an Issue comment. Do not
modify the Issue body, run Git operations, or push changes. Update
documentation only when behavior or architecture changes.
