---
description: Migrate local task folders to GitHub Issues without deleting them
subtask: true
---

Load `github-issues`. Discover `dev_items/` folders matching
`NNN-*`, read each `task.md`, convert its metadata and body using
`.opencode/templates/issue-task.md`, and create one Issue per item. Map local
statuses `new`, `commited`, `done`, and `block` to `Ready`, `In progress`,
`Done`, and `Blocked`. Optionally copy summaries to the local support directory
and post them as comments. Never delete or modify the source task folders. Print
a table containing successes and failures.
