---
description: Run a script or command on the configured remote host
agent: cluster
subtask: true
---

Execute the following workflow exactly:

1. Load `cluster-ssh`. Load `windows-credential-manager` only when configured.
2. Require a user-supplied command after `$ARGUMENTS`; never invent a command.
3. Load the configured env file and require `OPENCODE_CLUSTER_USER`,
   `OPENCODE_CLUSTER_HOST`, and `OPENCODE_CLUSTER_ROOT`. Ask about missing
   values before connecting.
4. Verify the remote root with `test -d`.
5. Run only the explicitly supplied command from `OPENCODE_CLUSTER_ROOT`.
6. Activate `OPENCODE_CLUSTER_VENV` first when it is configured.
7. Use the existing `OPENCODE_CLUSTER_SCREEN` session for long-running work.
   Never create or interrupt a screen session automatically.
8. Retry one failed SSH connection, then report the standard connection failure.
