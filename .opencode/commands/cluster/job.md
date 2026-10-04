---
description: Execute a user-described multi-step remote job safely
agent: cluster
subtask: true
---

Execute the following workflow exactly:

1. Load `cluster-ssh` for remote commands and `cluster-scp` for transfers.
2. Load `windows-credential-manager` only when configured.
3. Load the env file and resolve all `OPENCODE_CLUSTER_*` values before
   connecting. Ask for missing values and confirm whether they are temporary or
   externally configured.
4. Verify `OPENCODE_CLUSTER_ROOT` before every remote operation and keep every
   path under that root.
5. Plan the requested steps, showing transfer and command actions before doing
   them when the job has more than one operation.
6. Do not run `rm`, `rmdir`, `mv`, overwrite existing data, or terminate a
   process without explicit confirmation for that exact action.
7. Use only an existing configured screen session. Never create or interrupt a
   screen session automatically.
8. Apply the SSH/SCP one-retry rule and stop on a second connection failure.
