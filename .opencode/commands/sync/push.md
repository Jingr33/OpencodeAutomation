---
description: Commit, push, and optionally create a pull request for the active branch
agent: sync
subtask: true
---

Description:
You must push relevant code from local to remote repository and doo all the steps below.

Dependecies:
Load `github-issues`.
Steps:
1. Inspect status, current branch, remote, and related Issue
before acting.
2. Resolve and record the repository's actual default branch without
assuming `main` or `master` (but can be different).
3. Stage only intended changes, use an Issue-aware
commit message when possible, push the current branch, and create a PR only when
one does not already exist.
4. Never place credentials in a remote URL.
5. Ask before
force-pushing (prefer force-with-lease) or committing unrelated changes.
6. - After the push and any requested PR action succeed and are verified, return the
current checkout to the resolved default branch with
`git switch <resolved-default-branch>`.
   - If no push occurred, leave the current
branch unchanged. If the default branch is already checked out by
another worktree, do not force a switch or alter that worktree; report the
condition and leave the current checkout unchanged.
