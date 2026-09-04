---
description: Create a GitHub Issue, optionally add it to a project
subtask: true
---

Load `github-issues` skill. Treat all text after the command
as the Issue description. Parse optional `--type <feature|bug|hotfix>` and
`--scope <scope>`, defaulting to `feature` and `repository`. Read
`.opencode/templates/issue-task.md`, create the Issue in the resolved repository,
and optionally add it to the configured GitHub Project with status `Backlog`.
Stop after reporting the Issue URL and title. Do not create a branch, worktree,
or any other repository state. Branch and worktree creation is the
responsibility of the dev and CR commands that operate on the Issue later.
