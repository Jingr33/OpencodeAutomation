---
description: Find and optionally remove worktrees whose pull requests are closed
subtask: true
---

Load the `worktree` skill. Preview candidates first:

```bash
python .opencode/scripts/worktree.py cleanup --closed-prs --repo <path>
```

Check every candidate's dirty state and closed PR. Only after user confirmation
run the same command with `--apply`; use `--force` only for explicitly approved
dirty worktrees. For each removed worktree, also remove it from the VS Code
workspace with `python .opencode/scripts/workspace.py remove <path>`. Prune
stale Git worktree metadata and report skipped candidates.
