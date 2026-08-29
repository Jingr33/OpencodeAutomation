---
description: Inspect and synchronize dependencies on a configured remote project
agent: cluster
subtask: true
---

Load `cluster-ssh`, `cluster-scp`, and `package-management`. Detect the active
repository's dependency manifests and package manager instead of assuming
`requirements.txt` or Python. Show proposed local and remote changes before
installing anything. Do not modify a remote environment without explicit user
approval.
