---
description: Upload a local file or folder to the configured remote host
agent: cluster
subtask: true
---

Execute the following workflow exactly:

1. Load `cluster-scp`. Load `windows-credential-manager` only when
   `OPENCODE_CLUSTER_AUTH=windows-credential-manager`.
2. If `$ARGUMENTS` is empty, stop with:
   `no target specified, usage: cluster.push <local-path>`.
3. Parse the first whitespace-separated token as `localPath`. Do not interpret a
   later `to <path>` token as a destination.
4. Resolve `localPath` from the active repository/worktree root, never from the
   automation framework directory. Verify it exists.
5. Load `OPENCODE_CLUSTER_ENV_FILE`, or `.opencode/.env` in the active
   repository when the override is unset. Parse only `KEY=VALUE` lines.
6. Require `OPENCODE_CLUSTER_USER`, `OPENCODE_CLUSTER_HOST`, and
   `OPENCODE_CLUSTER_ROOT`. Ask for each missing value and confirm whether it is
   temporary or should be configured externally. Do not connect while any value
   is missing.
7. If `localPath` is a directory, upload its contents directly into
   `OPENCODE_CLUSTER_ROOT` by default. Use the directory itself below the root
   only when the later arguments contain the explicit word `mirror`.
8. Verify the remote parent with SSH, then transfer with `scp` or the configured
   `OPENCODE_CLUSTER_SCP_COMMAND` wrapper. Use `-r` for directories and never
   pass a password.
9. Retry one failed transfer. If it fails again, stop with:
   `connection closed, unable to connect to remote server`.
