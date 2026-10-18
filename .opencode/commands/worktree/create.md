---
description: Create an isolated worktree and branch for a task
subtask: true
---

Load the `worktree` skill. This command is for external or managed target
repositories only. It MUST NOT be used for the agentic repository; the helper
will reject that target. Parse `$ARGUMENTS` as `<branch> [base]`, with optional
`--repo <path>` and `--path <path>`. `<repo>` MUST be the registered repository
checkout (`repository.py list`), never a task worktree. Run:

```bash
python .opencode/scripts/worktree.py create <branch> [base] [--repo <path>] [--path <path>]
```

The new worktree MUST be created directly under the framework worktree root
(`OPENCODE_WORKTREE_ROOT` or the `.worktrees/` directory) as a first-level
sibling of the repository checkout: `<worktree-root>/<sanitized-branch>`. Never
place a worktree inside another worktree or inside a repository checkout;
nested paths like `.worktrees/<repo>/.worktrees/<branch>` are forbidden and are
rejected by the helper. If the branch already exists, attach it instead of
creating a duplicate branch, but do not reuse a nested worktree silently; stop
and report it. Report the worktree path and branch only after verifying the path
is a direct child of the worktree root.
