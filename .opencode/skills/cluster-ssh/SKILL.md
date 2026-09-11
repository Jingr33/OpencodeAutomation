---
name: cluster-ssh
description: Executes explicitly requested commands on a configurable Linux cluster with root and virtualenv validation; use cluster-session for existing screen sessions
license: MIT
compatibility: opencode
---

Configuration is supplied through environment variables:

- `OPENCODE_CLUSTER_USER` and `OPENCODE_CLUSTER_HOST` are required.
- `OPENCODE_CLUSTER_ROOT` is the remote project root.
- `OPENCODE_CLUSTER_VENV` is an optional virtualenv path relative to the root.
- `OPENCODE_CLUSTER_SCREEN` is an optional screen session name.
- `OPENCODE_CLUSTER_SSH_COMMAND` can override the SSH client command.

## Mandatory Workflow

1. Confirm the requested command is explicit and determine whether it is a
   read-only preflight, a short direct command, or a long-running job.
2. Verify `OPENCODE_CLUSTER_USER`, `OPENCODE_CLUSTER_HOST`, and
   `OPENCODE_CLUSTER_ROOT`. Stop with `cluster configuration is incomplete` if
   any required value is missing.
3. Build the endpoint from the configured user and host. Never use a host,
   user, password, or path from an example or from another repository.
4. Verify connectivity and the remote root before running the requested
   command. Stop with `cannot find the configured remote root` when the root
   cannot be verified.
5. Start every remote command with the configured root as its working
   directory. A configured `OPENCODE_CLUSTER_VENV` is relative to that root;
   verify it exists and activate it before running Python or package commands.
   Stop with `unable to use configured virtual environment` if validation or
   activation fails.
6. Run only the command explicitly requested by the user. Do not append
   cleanup, synchronization, package installation, or process-control steps.
7. For screen work, load `cluster-session` and follow its exact existing-session
   workflow. This skill never creates, interrupts, detaches, or kills sessions.
8. Retry one failed connection or command only when the failure is transient;
   otherwise report the original command, failure, and partial result.

Keep all paths below `OPENCODE_CLUSTER_ROOT`, require confirmation before
destructive commands, and use key-based authentication or the user's SSH agent.
Never expose passwords or private keys in prompts, files, or command output.
