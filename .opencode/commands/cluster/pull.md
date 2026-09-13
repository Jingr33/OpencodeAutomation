---
description: Download a file or folder from a configured Linux cluster
agent: cluster
subtask: true
---

Load `cluster-ssh` for the remote preflight and `cluster-scp` for the transfer.

Follow these steps:

1. If `$ARGUMENTS` is empty, stop with
   `no target specified, usage: cluster/pull <remote-relative-path> [files-only]`.
2. Parse the first whitespace-separated token as the remote path. Treat the
   remaining text as options; recognize `files-only`, `files only`, and
   `direct files` as the direct-files mode. Reject absolute paths and paths
   containing `..` that would escape `OPENCODE_CLUSTER_ROOT`.
3. Validate `OPENCODE_CLUSTER_USER`, `OPENCODE_CLUSTER_HOST`, and
   `OPENCODE_CLUSTER_ROOT` through `cluster-ssh`. SSH to the configured host
   and verify `<remote-root>/<remote-path>` with `test -e`. If it is missing,
   stop with `cannot find the remote target`.
4. Map the remote path to the same relative local path. Verify the local parent
   exists or can be created without deleting anything. If the destination
   already exists, show it and request confirmation before any overwrite or
   merging into it.
5. In normal mode, transfer the verified file or directory recursively as
   appropriate. In `files-only` mode, first list only direct regular files in
   the remote directory, then transfer each file individually to the matching
   local directory; do not transfer subdirectories.
6. Use `cluster-scp` for the transfer and its one retry. Do not remove local
   targets. If a transfer fails after retry, report the exact remote file,
   local target, and whether earlier files completed.
7. Verify the local result and report the files downloaded and any skipped
   entries.
