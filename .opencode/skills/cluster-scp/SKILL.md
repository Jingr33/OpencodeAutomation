---
name: cluster-scp
description: Transfers files between the active repository and a configurable Linux cluster root with checked path mapping and retry behavior
license: MIT
compatibility: opencode
---

## Mandatory Workflow

1. Verify `OPENCODE_CLUSTER_USER`, `OPENCODE_CLUSTER_HOST`, and
   `OPENCODE_CLUSTER_ROOT`. Stop with `cluster configuration is incomplete` if
   any value is missing.
2. Parse the local or remote path as a path relative to the appropriate root.
   Reject absolute paths and `..` components that escape the root. Never infer
   a path from a host-specific example.
3. For uploads, verify the local source exists, calculate the remote target,
   verify its remote parent, and show the mapping before transferring.
4. For downloads, verify the remote source exists, calculate the local target,
   verify its local parent, and show the mapping before transferring.
5. Mirror the path below `OPENCODE_CLUSTER_ROOT` by default. In explicit `root`
   mode, copy a directory's contents directly into the remote root instead of
   adding the source directory name.
6. If the transfer would overwrite an existing target, stop and request
   confirmation. Never remove local data or use a destructive remote command to
   make a transfer work.
7. Retry one failed transfer. If the retry fails, report
   `connection closed, unable to connect to remote server` and include the
   source, target, and partial-transfer state.

Use key-based authentication or the user's SSH agent. Never store or request a
password in this skill, prompt, command file, or transfer log.
