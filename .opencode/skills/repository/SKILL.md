---
name: repository
description: Registers and clones arbitrary Git repositories into the framework workspace
license: MIT
compatibility: opencode
---

Use `.opencode/scripts/repository.py` for repository registration. Managed
repositories are cloned below `source/<name>_slot0`; the root may be changed
with `OPENCODE_SOURCE_ROOT` or `--path`. Keep cloned repositories outside the
framework Git history. Verify the remote and default branch after cloning. A registered
repository becomes the target for later commands by passing its path or setting
`OPENCODE_GITHUB_REPO`.
