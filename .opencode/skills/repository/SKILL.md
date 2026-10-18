---
name: repository
description: Registers and clones arbitrary Git repositories into the framework workspace
license: MIT
compatibility: opencode
---

Use `.opencode/scripts/repository.py` for repository registration. Clone
repositories into the first-level workspace layout as `.worktrees/<name>` by
passing `--path .worktrees/<name>`; keep them outside the framework Git history.
Verify the remote and default branch after cloning. A registered repository
becomes the target for later commands by passing its path or setting
`OPENCODE_GITHUB_REPO`. Task worktrees of a registered repository are always
created as first-level siblings under `.worktrees/`, never inside the repository
checkout. Clones are made accessible to every local account (`Everyone` full
control on Windows, `a+rwX` on POSIX).
