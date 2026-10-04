---
name: cluster-scp
description: Transfers files between the active repository and a configurable remote project root
license: MIT
compatibility: opencode
---

# SCP Workflow

Run these steps in order for every transfer.

1. Find `repoRoot` with `git rev-parse --show-toplevel`. Resolve relative local
   paths from `repoRoot`, not from the automation framework directory.

2. Load configuration exactly as described by `cluster-ssh`:
   - Use `OPENCODE_CLUSTER_ENV_FILE` when set, otherwise `repoRoot/.opencode/.env`.
   - Parse simple `KEY=VALUE` lines without executing or printing the file.
   - Process environment variables override file values.
   - Require `OPENCODE_CLUSTER_USER`, `OPENCODE_CLUSTER_HOST`, and
     `OPENCODE_CLUSTER_ROOT` before connecting. Ask for missing values and
     confirm whether they are temporary or externally configured.

3. Select commands:
   ```text
   sshCommand = OPENCODE_CLUSTER_SSH_COMMAND or `ssh`
   scpCommand = OPENCODE_CLUSTER_SCP_COMMAND or `scp`
   target = OPENCODE_CLUSTER_USER + "@" + OPENCODE_CLUSTER_HOST
   ```
    When `OPENCODE_CLUSTER_AUTH=windows-credential-manager`, load
    `windows-credential-manager` and require the configured SSH/SCP helpers.
    Never put a password in either command.

    File transfer must use `scpCommand` and must not be replaced with an SSH
    shell command, `sftp`, or an unrequested synchronization tool. SSH is only
    for remote verification.

4. Parse the transfer arguments:
   - For `cluster.push`, parse the first token as the local source.
   - For `cluster.pull`, parse the first token as a path relative to the remote
     root.
   - Treat all later tokens as instructions, not as a destination override.
   - Reject absolute paths and paths containing `..` that escape the selected
     repository or remote root.

5. For `cluster.push`, resolve and verify the local source:
   ```text
   localSource = repoRoot / parsedSource
   ```
   Stop with `cannot find the target folder` if it does not exist.

6. Choose the upload destination:
   - A file uploads to `OPENCODE_CLUSTER_ROOT/<relative source path>`.
   - A directory uploads its contents directly to `OPENCODE_CLUSTER_ROOT` by
     default, equivalent to `scp -r <directory>/. <root>/`.
   - Only an explicit `mirror` instruction uploads the directory itself below
     the root, equivalent to `scp -r <directory> <root>/<basename>`.
   - Never require `root` and never honor a trailing `to <path>` destination.

7. For `cluster.pull`, set:
   ```text
   remoteSource = OPENCODE_CLUSTER_ROOT / parsedRemotePath
   localTarget = repoRoot / parsedRemotePath
   ```
   Verify `remoteSource` with SSH before downloading. Verify the local parent.
   If `localTarget` already exists, ask before overwriting or deleting it.

8. Verify the remote parent for an upload before invoking SCP:
   ```bash
   <sshCommand> <target> "test -d -- <quoted remote parent>"
   ```
   Stop with `remote parent is unavailable` if the check fails.

9. Invoke `scpCommand` with separately quoted arguments. Add `-r` only for
   directories. Do not concatenate untrusted paths into a shell command.

10. If the transfer fails, retry the same transfer exactly once. If the retry
   fails, stop with:
   `connection closed, unable to connect to remote server`.

## SCP Command Patterns

Use these exact argument patterns. `scpCommand` is either `scp` or the
configured Credential Manager-aware wrapper. `target` is
`<user>@<host>`. Keep every local and remote path as a separate argument.

### Push One File

```text
scpCommand <options> "<localFile>" "<target>:<remoteRoot>/<fileName>"
```

### Push Directory Contents

Use this for the default directory upload. The directory itself must not become
a nested remote directory:

```text
scpCommand -r <options> "<localDirectory>/." "<target>:<remoteRoot>/"
```

On clients that do not support the `/.` source form, enumerate the directory
contents and pass them as separate SCP source arguments:

```text
scpCommand -r <options> "<localDirectory>/<entry1>" "<localDirectory>/<entry2>" "<target>:<remoteRoot>/"
```

### Push Directory As A Nested Directory

Use only when the user explicitly requests `mirror`:

```text
scpCommand -r <options> "<localDirectory>" "<target>:<remoteRoot>/<directoryName>"
```

### Pull One File

```text
scpCommand <options> "<target>:<remoteRoot>/<remoteFile>" "<localFile>"
```

### Pull A Directory

```text
scpCommand -r <options> "<target>:<remoteRoot>/<remoteDirectory>" "<localParentDirectory>/"
```

For every pattern, verify the remote parent with SSH before invoking SCP, use
the configured helper when Credential Manager authentication is selected, and
never add a password argument or interpolate a password into the command.
