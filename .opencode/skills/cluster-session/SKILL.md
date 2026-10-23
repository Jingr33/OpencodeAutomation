---
name: cluster-session
description: Uses an existing Linux screen session on a configured cluster for long-running commands; use when a cluster prompt mentions screen, sessions, training, jobs, or other work that may outlive SSH.
license: MIT
compatibility: opencode
---

# Linux Cluster Sessions

Use this skill with `cluster-ssh` when a remote command should continue after
the SSH client disconnects or when the user explicitly requests `screen`.
`OPENCODE_CLUSTER_SCREEN` must contain the configured existing session name.

## Required Workflow

1. Load `cluster-ssh` and validate `OPENCODE_CLUSTER_USER`,
   `OPENCODE_CLUSTER_HOST`, `OPENCODE_CLUSTER_ROOT`, and
   `OPENCODE_CLUSTER_SCREEN` before touching the remote session.
2. Connect to the configured host and verify the remote root exists.
3. Check for the exact configured session:

   ```bash
   screen -ls
   screen -S "$OPENCODE_CLUSTER_SCREEN" -Q windows
   ```

4. If the session does not exist, stop with `no available screen to use`.
   Never create a session, rename one, kill one, detach another client, or
   interrupt a process automatically.
5. Inspect the current session output before sending a command. If it is not
   clearly idle at a shell prompt, stop and report that the session is busy.
   Do not send control characters to make it idle.

   A non-interactive inspection can use a temporary hardcopy file:

   ```bash
   tmp_screen_output="${TMPDIR:-/tmp}/opencode-screen-$$.log"
   screen -S "$OPENCODE_CLUSTER_SCREEN" -X hardcopy -h "$tmp_screen_output"
   tail -n 40 "$tmp_screen_output"
   ```

6. Use the existing session only after the command, working directory, virtual
   environment, and expected duration have been shown to the user. The command
   must start below `OPENCODE_CLUSTER_ROOT` and activate
   `OPENCODE_CLUSTER_VENV` only when it is configured and verified.
7. Submit the explicitly approved, shell-escaped command to the selected shell
   window without sending control characters:

   ```bash
   screen -S "$OPENCODE_CLUSTER_SCREEN" -p <window> -X stuff "$safe_command$(printf '\r')"
   ```

   Do not assume a window when `screen -Q windows` reports more than one; ask
   which configured window is the target. Never send a command to a busy window.
8. Monitor output with another non-interrupting hardcopy and report completion,
   failure, or the last observed output. Do not poll by pressing Enter, Ctrl-C,
   Ctrl-D, or any other control key.

## Direct SSH Fallback

Use direct SSH instead of screen only when the user explicitly requests
`without screen` or the operation is a short, read-only preflight. If a task
may run for more than a few minutes and no screen session is available, stop and
ask rather than silently starting one or running an unprotected job.

## Safety

- Keep all commands and paths below `OPENCODE_CLUSTER_ROOT`.
- Do not reuse a session name supplied by the user unless it matches the
  configured value, unless the user explicitly approves the override.
- Do not run destructive commands, package installation, or process control
  without showing the command and receiving explicit approval.
- Never put passwords, private keys, or host-specific defaults in this skill.
