---
description: Migrate remaining local task folders to GitHub Issues
subtask: true
---

Load `github-issues`. Discover any remaining `dev_items/` or `issues/` folders
matching `NNN-*`, read each `task.md` or `issue.md`, convert its metadata and
body using `.opencode/templates/issue-task.md`, and create one GitHub Issue per
item. Map local statuses `new`, `commited`, `done`, and `block` to `Ready`,
`In progress`, `Done`, and `Blocked`. Post summaries as Issue comments. Never
delete or modify the source folders. Print a table containing successes and
failures. Skip items that already have a corresponding GitHub Issue.
