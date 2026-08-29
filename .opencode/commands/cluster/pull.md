---
description: Download a file or folder from the configured remote host
agent: cluster
subtask: true
---

Load `cluster-ssh` and `cluster-scp`. Parse the first token as a path relative to
`OPENCODE_CLUSTER_ROOT`, verify it remotely, and download it to the matching local
relative path. Do not delete an existing local target without confirmation.
