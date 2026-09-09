---
description: Find and optionally remove obsolete worktrees and local branches
subtask: true
---

Load the `worktree` skill. Preview candidates first:

```bash
python .opencode/scripts/worktree.py cleanup --closed-prs --repo <path>
```

Check every candidate's dirty state and closed PR. Only after user confirmation
run the same command with `--apply`; use `--force` only for explicitly approved
dirty worktrees. The apply operation also removes local branches whose PR was
merged into the default branch and whose local tip is at or behind its remote
copy. It protects the current branch, active worktrees, unsafe worktrees, and
branches with newer local commits. For each removed worktree, also remove it
from the VS Code workspace with `python .opencode/scripts/workspace.py remove
<path>`. Prune stale Git worktree metadata and report skipped candidates.
