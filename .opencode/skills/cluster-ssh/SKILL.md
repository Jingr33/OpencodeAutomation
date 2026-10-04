---
name: cluster-ssh
description: Executes explicitly requested commands on a configurable remote host with optional virtualenv and screen setup
license: MIT
compatibility: opencode
---

# SSH Workflow

Run these steps in order for every SSH operation. Do not skip configuration or
verification because the requested command appears harmless.

1. Find the active repository root:
   ```text
   repoRoot = `git rev-parse --show-toplevel`
   ```
   Resolve all relative local paths from `repoRoot`, never from the automation
   framework directory.

2. Select the configuration file:
   - If `OPENCODE_CLUSTER_ENV_FILE` is set, resolve it relative to `repoRoot`
     unless it is absolute.
   - Otherwise use `repoRoot/.opencode/.env` when that file exists.
   - Read only non-empty `KEY=VALUE` lines. Never execute the file, print it, or
     include its contents in a prompt or command log.
   - Process environment variables override values from the file.

3. Require these values before connecting:
   - `OPENCODE_CLUSTER_USER`
   - `OPENCODE_CLUSTER_HOST`
   - `OPENCODE_CLUSTER_ROOT`
   If a value is missing, call the question tool, ask for that value, and ask
   whether it is for this operation only or should be configured externally.
   Do not connect until every required value is available.

4. Select authentication:
   - If `OPENCODE_CLUSTER_AUTH=windows-credential-manager`, load
     `windows-credential-manager` and require a configured
     `OPENCODE_CLUSTER_SSH_COMMAND` helper.
   - Otherwise use the configured SSH command, SSH key, or SSH agent.
   - Never request, interpolate, log, or save an SSH password.

5. Build the SSH invocation:
   ```text
   sshCommand = OPENCODE_CLUSTER_SSH_COMMAND or `ssh`
   target = OPENCODE_CLUSTER_USER + "@" + OPENCODE_CLUSTER_HOST
   ```
   Pass the remote command as a separately quoted argument. Do not build a
   shell command by concatenating untrusted user input.

6. Verify the remote root before running the requested operation:
   ```bash
   <sshCommand> <target> "test -d -- <quoted OPENCODE_CLUSTER_ROOT>"
   ```
   If this check fails, stop with `remote project root is unavailable`.

7. Run the requested command from the remote root. Use:
   ```bash
   <sshCommand> <target> "cd -- <quoted OPENCODE_CLUSTER_ROOT> && <approved command>"
   ```
   Activate the virtual environment only when `OPENCODE_CLUSTER_VENV` is set:
   ```bash
   . <quoted OPENCODE_CLUSTER_ROOT>/<quoted OPENCODE_CLUSTER_VENV>/bin/activate
   ```

8. For long-running work, use the existing session named by
   `OPENCODE_CLUSTER_SCREEN`. Never create, detach, interrupt, or reuse a
   session that is already running another process without explicit approval.

9. If the SSH connection or command transport fails, retry the same operation
   exactly once. If the retry fails, stop with:
   `connection closed, unable to connect to remote server`.
