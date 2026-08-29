---
description: Upload a local file or folder to the configured remote host
agent: cluster
subtask: true
---

Load `cluster-scp`. If no path is supplied, stop with
`no target specified, usage: cluster.push <local-path>`. Parse the first token as
the local path. Mirror it below `OPENCODE_CLUSTER_ROOT` by default; if the user
explicitly says `root`, upload its contents to the remote root. Verify the local
path and remote parent before transferring.
