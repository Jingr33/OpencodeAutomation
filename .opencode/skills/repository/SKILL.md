---
name: repository
description: Registers and clones arbitrary Git repositories into the framework workspace
license: MIT
compatibility: opencode
---

Use `.opencode/scripts/repository.py` for repository registration. Repositories
default to `repositories/<name>` and may be placed elsewhere with
`OPENCODE_REPO_ROOT` or `--path`. Keep cloned repositories outside the framework
Git history. Verify the remote and default branch after cloning. A registered
repository becomes the target for later commands by passing its path or setting
`OPENCODE_GITHUB_REPO`.
