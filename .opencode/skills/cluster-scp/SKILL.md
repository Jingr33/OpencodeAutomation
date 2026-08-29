---
name: cluster-scp
description: Transfers files between the active repository and a configurable remote project root
license: MIT
compatibility: opencode
---

Use `OPENCODE_CLUSTER_USER`, `OPENCODE_CLUSTER_HOST`, and
`OPENCODE_CLUSTER_ROOT`. Mirror relative paths by default and require an
explicit `root` mode to copy a directory's contents into the remote root.
Verify remote parents before upload and local parents before download. Use key-
based authentication or the SSH agent; never store a password in this skill.
Retry one failed transfer, then report the connection failure. Do not delete
existing local data as part of a download without confirmation.
