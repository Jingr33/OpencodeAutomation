---
description: Execute a user-described multi-step remote job safely
agent: cluster
subtask: true
---

Load `cluster-ssh` and `cluster-scp` as needed. Keep all remote work under
`OPENCODE_CLUSTER_ROOT`. Do not run `rm`, `rmdir`, `mv`, overwrite, or terminate
processes without explicit confirmation. Never create or interrupt screen
sessions automatically. Stop and ask when remote configuration is incomplete.
