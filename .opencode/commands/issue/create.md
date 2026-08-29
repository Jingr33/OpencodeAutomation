---
description: Create a GitHub Issue, optionally add it to a project, and create its branch
subtask: true
---

Load `github-issues` skill. Treat all text after the command
as the Issue description. Parse optional `--type <feature|bug|hotfix>` and
`--scope <scope>`, defaulting to `feature` and `repository`. Read
`.opencode/templates/issue-task.md`, create the Issue in the resolved repository,
optionally add it to the configured GitHub Project with status `Ready`, then use
`/worktree.create <issue-number>-<slug>` to create and switch to its branch.
Stop after reporting the Issue URL and worktree path. Do not implement the task.
