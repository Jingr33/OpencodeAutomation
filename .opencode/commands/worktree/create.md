---
description: Create an isolated worktree and branch for a task
subtask: true
---

Load the `worktree` skill. This command is for external or managed target
repositories only. It MUST NOT be used for the agentic repository; the helper
will reject that target. Parse `$ARGUMENTS` as `<branch> [base]`, with optional
`--repo <path>` and `--path <path>`. Run:

```bash
python .opencode/scripts/worktree.py create <branch> [base] [--repo <path>] [--path <path>]
```

If the branch already exists, attach it instead of creating a duplicate branch.
If no path is supplied, use `OPENCODE_WORKTREE_ROOT` or `.worktrees/`. Report the
worktree path and branch. If no free worktree exists, create a new one; do not
silently reuse another active branch.
