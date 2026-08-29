---
description: Commit, push, and optionally create a pull request for the active branch
agent: sync
subtask: true
---

Load `github-issues`. Inspect status, current branch, remote,
and related Issue before acting. Stage only intended changes, use an Issue-aware
commit message when possible, push the current branch, and create a PR only when
one does not already exist. Never place credentials in a remote URL. Ask before
force-pushing or committing unrelated changes.
