---
description: Stage, commit, push, and create a pull request for reviewed changes
agent: sync
subtask: true
---

Description:
You must ship new changes properly from unstaged or untracked changes in git to PR with according PR summary and prepare the changes to be merged. Run the full synchronization workflow for the active branch.

Dependencies:
Load `github-management` when review metadata is involved.

Steps:
1. Use a summary from the
configured local support directory when available; otherwise write a concise PR
body from the diff.
2. Resolve the repository's actual default branch without
assuming `main` or `master` (but can be different).
3. After the push and PR creation succeed and are
verified, return the current checkout to that default branch with
`git switch <resolved-default-branch>`.
4. If no push occurred, leave the current
branch unchanged. If the default branch is already checked out by another
worktree, do not force a switch or alter that worktree;
report the condition and leave the current checkout unchanged.
5. Confirm the
final branch and PR URL.
