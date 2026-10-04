---
description: Download a file or folder from the configured remote host
agent: cluster
subtask: true
---

Execute the following workflow exactly:

1. Load `cluster-ssh` and `cluster-scp`. Load
   `windows-credential-manager` only when configured.
2. If `$ARGUMENTS` is empty, stop with:
   `no target specified, usage: cluster.pull <remote-path>`.
3. Parse the first whitespace-separated token as `remotePath`. Treat it as
   relative to `OPENCODE_CLUSTER_ROOT`; reject absolute paths and root escapes.
4. Load `OPENCODE_CLUSTER_ENV_FILE`, or the active repository's
   `.opencode/.env`, and require `OPENCODE_CLUSTER_USER`,
   `OPENCODE_CLUSTER_HOST`, and `OPENCODE_CLUSTER_ROOT`. Ask about missing
   values before connecting.
5. Verify `OPENCODE_CLUSTER_ROOT/<remotePath>` over SSH. Stop with
   `cannot find the target folder` when it does not exist.
6. Set the local destination to the same relative path under the active
   repository/worktree. Verify its parent exists. If the destination exists,
   ask before overwriting or deleting anything.
7. Invoke `scp` or the configured `OPENCODE_CLUSTER_SCP_COMMAND` wrapper, using
   `-r` when the remote source is a directory. Do not expose or interpolate
   passwords.
8. Retry one failed transfer. If it fails again, stop with:
   `connection closed, unable to connect to remote server`.
