---
description: Upload the contents of a local directory to the configured remote root
agent: cluster
subtask: true
---

Load `cluster-scp`. Use the first argument as the local directory to upload; when
no argument is supplied, use `src`. Verify that the directory exists and that
`OPENCODE_CLUSTER_ROOT` is configured before acting. Upload the directory's
contents to the remote root, not the directory itself, so a local
`src/trainers/model.py` becomes `<remote-root>/trainers/model.py`. Show the local
and remote paths before transferring and stop if the remote parent cannot be
verified.
