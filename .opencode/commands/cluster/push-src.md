---
description: Upload a local directory's contents to a configured Linux cluster root
agent: cluster
subtask: true
---

Load `cluster-scp`.

Follow these steps:

1. Parse `$ARGUMENTS` as the local directory path. When it is empty, use `src`.
   Ignore no extra words silently; if more text is supplied, treat it as an
   instruction only when it is explicitly understood and otherwise ask.
2. Verify the local directory with `test -d` semantics. If it is missing, stop
   with `cannot find the local source directory`.
3. Validate `OPENCODE_CLUSTER_USER`, `OPENCODE_CLUSTER_HOST`, and
   `OPENCODE_CLUSTER_ROOT`. Verify the remote root exists before transferring.
4. Use explicit root mode from `cluster-scp`: upload the directory's contents,
   not the directory itself. For example, local
   `src/trainers/model.py` becomes `<remote-root>/trainers/model.py`, never
   `<remote-root>/src/trainers/model.py`.
5. Show the source directory, remote root, mapping rule, and existing-target
   check. Request confirmation before overwriting remote files.
6. Transfer recursively with `cluster-scp`, preserving relative subdirectories
   and retrying one failed transfer. Do not remove or replace remote files to
   make the transfer work.
7. Verify the remote result and report the number of transferred entries and
   any partial failure.
