---
description: Remove one isolated worktree safely
subtask: true
---

Load the `worktree` skill. Identify the exact path or branch and show its status.
After explicit user confirmation, first remove the worktree from the VS Code
workspace with `python .opencode/scripts/workspace.py remove <path-or-branch>`,
then run:

```bash
python .opencode/scripts/worktree.py remove <path-or-branch> --repo <path>
```

Add `--force` only when the user explicitly requests removal of uncommitted
changes. Never remove the main worktree.
