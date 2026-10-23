---
description: Run an explicit command on a configured Linux cluster
agent: cluster
subtask: true
---

Load `cluster-ssh`. Load `cluster-session` when the request mentions `screen`,
an existing session, training, a server, a watcher, or another long-running
operation.

Follow these steps:

1. If `$ARGUMENTS` is empty, stop with
   `no command specified, usage: cluster/run <command>`.
2. Preserve `$ARGUMENTS` as the exact command string. Do not replace it with a
   guessed script, add flags, or append cleanup. If the requested command is
   destructive or its target is ambiguous, show the command and ask for
   confirmation before connecting.
3. Validate `OPENCODE_CLUSTER_USER`, `OPENCODE_CLUSTER_HOST`, and
   `OPENCODE_CLUSTER_ROOT`. Verify the remote root exists and establish the
   root-contained working directory.
4. If `OPENCODE_CLUSTER_VENV` is configured, verify the path relative to the
   remote root and activate it before the command. Stop with
   `unable to use configured virtual environment` if this fails.
5. Choose execution mode explicitly:
   - For a short read-only command, run it directly over SSH.
   - For a long-running or user-requested session command, load
     `cluster-session`, verify the configured existing screen session is
     present and idle, and run inside it.
   - If the mode is ambiguous, ask instead of guessing.
6. Capture bounded stdout, stderr, and the exit status for direct execution.
   For screen execution, monitor without sending interrupts and report the
   last observed output and session name.
7. Report the exact command, execution mode, configured root, exit/result
   status, and any output or timeout. Never create, detach, interrupt, or kill
   a screen session automatically.
