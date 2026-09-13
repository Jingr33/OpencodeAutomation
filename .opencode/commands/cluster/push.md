---
description: Upload a local file or folder to a configured Linux cluster
agent: cluster
subtask: true
---

Load `cluster-scp`.

Follow these steps:

1. If `$ARGUMENTS` is empty, stop with
   `no target specified, usage: cluster/push <local-path> [root]`.
2. Parse the first whitespace-separated token as the local path. Treat the
   remaining text as options. Only an explicit `root` or `root mode` changes
   the destination mapping; do not infer root mode from the basename.
3. Verify the local source exists. If it is missing, stop with
   `cannot find the local target`. Reject paths that resolve outside the active
   repository unless the user explicitly confirms the external path.
4. Validate the cluster configuration and calculate the destination:
   - Default mode mirrors `local/path` below `OPENCODE_CLUSTER_ROOT`.
   - Root mode uploads a file as `<remote-root>/<basename>` or a directory's
     contents directly below `<remote-root>`.
5. Show the local source, remote destination, transfer mode, and whether the
   target already exists. Request confirmation before any remote overwrite or
   file or directory.
6. Verify the remote parent with `cluster-ssh`, then transfer with
   `cluster-scp`. Preserve recursive directory structure and retry one failed
   transfer only.
7. Verify the remote result and report the mapping, transferred entries, and
   any partial failure. Do not delete or move remote data to make the upload
   succeed.
