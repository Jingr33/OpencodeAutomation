---
name: worktree
description: Creates, lists, reuses, and safely cleans concurrent Git worktrees
license: MIT
compatibility: opencode
---

Use `.opencode/scripts/worktree.py` rather than manually constructing worktree
paths. The helper stores worktrees outside the main checkout by default, creates
branches from an explicit base, and refuses to remove dirty worktrees unless
`--force` is given. `cleanup --closed-prs` can discover branches with closed
GitHub pull requests through `gh`; review its proposed removals before using
`--apply`.
