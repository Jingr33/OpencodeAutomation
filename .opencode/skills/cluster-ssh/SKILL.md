---
name: cluster-ssh
description: Executes explicitly requested commands on a configurable remote host with optional virtualenv and screen setup
license: MIT
compatibility: opencode
---

Configuration is supplied through environment variables:

- `OPENCODE_CLUSTER_USER` and `OPENCODE_CLUSTER_HOST` are required.
- `OPENCODE_CLUSTER_ROOT` is the remote project root.
- `OPENCODE_CLUSTER_VENV` is an optional virtualenv path relative to the root.
- `OPENCODE_CLUSTER_SCREEN` is an optional screen session name.
- `OPENCODE_CLUSTER_SSH_COMMAND` can override the SSH client command.

Verify the host and root before acting. Activate the virtual environment only if
configured. Use an existing screen session for long-running commands; never
create or interrupt one automatically. Do not expose passwords in prompts or
files. Configure key-based authentication or the user's SSH agent.
