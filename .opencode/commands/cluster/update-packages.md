---
description: Inspect and synchronize dependencies on a configured remote project
agent: cluster
subtask: true
---

Execute the following workflow exactly:

1. Load `cluster-ssh`, `cluster-scp`, and `package-management`.
2. Load `windows-credential-manager` only when configured.
3. Load cluster configuration and resolve missing values before connecting.
4. Inspect the active repository for dependency manifests and identify the
   package manager. Do not assume Python or `requirements.txt`.
5. Compare the local manifest and remote environment. Show the proposed changes
   and wait for explicit approval before installing anything.
6. Transfer only the approved manifest using `cluster-scp`.
7. Use `cluster-ssh` to run the package-manager synchronization under
   `OPENCODE_CLUSTER_ROOT`, activating the configured virtual environment first.
8. Verify the environment after installation and report any remaining import or
   dependency errors. Apply the one-retry rule only to connection failures.
