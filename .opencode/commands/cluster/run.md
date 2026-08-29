---
description: Run a script or command on the configured remote host
agent: cluster
subtask: true
---

Load `cluster-ssh`. Verify `OPENCODE_CLUSTER_USER`, `OPENCODE_CLUSTER_HOST`, and
`OPENCODE_CLUSTER_ROOT`. Change to the configured root, activate the configured
virtualenv if present, and run only the command explicitly provided by the user.
Use an existing configured screen session for long-running work.
