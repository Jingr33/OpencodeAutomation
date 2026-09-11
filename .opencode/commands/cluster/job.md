---
description: Execute a user-described multi-step job on a configured Linux cluster safely
agent: cluster
subtask: true
---

Load `cluster-ssh` for remote commands and `cluster-scp` for transfers. Load
`cluster-session` whenever the job is long-running, mentions `screen` or a
session, or may outlive the SSH connection.

Treat `$ARGUMENTS` as the complete user-described job. Do not invent missing
steps. Follow this workflow:

1. Parse the requested operations into local preparation, uploads, remote
   commands, and downloads. Identify every path, command, expected output, and
   whether each step is read-only or mutating.
2. If the request is ambiguous, destructive, or missing a required path,
   stop and ask one focused question. Do not guess a host, remote root, venv,
   screen name, or package manager.
3. Show the planned order, local-to-remote mappings, configured remote root,
   and direct-versus-screen execution mode before acting.
4. Load the relevant skills and validate all `OPENCODE_CLUSTER_*` settings.
   Verify the remote root before any transfer or command. Keep every remote
   path below that root.
5. Perform transfers with `cluster-scp`. Verify sources and parents first;
   request confirmation before overwriting an existing target.
6. Run commands with `cluster-ssh`. Start below the configured root and
   activate the configured virtualenv only after verifying it. Run only the
   commands present in the user's request.
7. For screen execution, follow `cluster-session` exactly: use the configured
   existing session only, inspect it for an idle shell, and stop if it is
   missing or busy. Never create, detach, interrupt, or kill a session.
8. Verify each step before starting the next dependent step. If a step fails,
   stop, preserve the partial result, and report the failed command and exact
   recovery point instead of continuing blindly.
9. Report the final status, files transferred, commands run, relevant output,
   and any steps that were skipped.

Never run `rm`, `rmdir`, `mv`, `chmod`, `chown`, package installation, process
control, or other destructive operations without showing the command, target,
impact, and receiving explicit confirmation.
