---
description: Remove a registered repository only after explicit confirmation
subtask: true
---

Load the `repository` skill. Show the repository path and dirty status first.
Remove it with `python .opencode/scripts/repository.py remove <name> --confirm`
only after the user explicitly confirms. Never remove a dirty repository or its
worktrees without `--force` and explicit confirmation.
