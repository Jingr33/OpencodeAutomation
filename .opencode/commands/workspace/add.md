---
description: Add a folder to the VS Code multi-root workspace
subtask: true
---

Run:

```bash
python .opencode/scripts/workspace.py add <path> [--name <name>]
```

This adds a task worktree or external repository folder to the workspace file
so it appears in VS Code alongside the agentic repository. The agentic repo is
always present; use this for external or managed target worktrees only.
