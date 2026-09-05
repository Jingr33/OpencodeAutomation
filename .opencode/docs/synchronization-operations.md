# Synchronization and Cluster Operations

This document defines the synchronization commands and cluster operation behavior
based on the actual command files in `.opencode/commands/sync/` and
`.opencode/commands/cluster/`.

## Synchronization Commands

### sync/pull

**Description:** Pull changes from the active repository remote.

**Behavior:**
- Inspects the current branch and working tree
- If clean, runs `git pull` for the active repository
- Does not discard local changes
- Reports the result

**Example:** `sync/pull`

---

### sync/push

**Description:** Commit, push, and optionally create a pull request for the active branch.

**Behavior:**
- Loads `github-issues` skill for Issue awareness
- Inspects status, current branch, remote, and related Issue before acting
- Stages only intended changes
- Uses an Issue-aware commit message when possible
- Pushes the current branch
- Creates a PR only when one does not already exist
- Never places credentials in a remote URL
- Asks before force-pushing or committing unrelated changes

**Example:** `sync/push`

---

### sync/ship

**Description:** Stage, commit, push, and create a pull request for reviewed changes.

**Behavior:**
- Runs the full synchronization workflow for the active branch
- Loads `github-management` when review metadata is involved
- Uses a summary from the configured local support directory when available
- Writes a concise PR body from the diff when no summary exists
- Confirms the final branch and PR URL

**Example:** `sync/ship`

---

## Cluster Operations

### cluster/job

**Description:** Execute a user-described multi-step remote job safely.

**Behavior:**
- Loads `cluster-ssh` and `cluster-scp` as needed
- Keeps all remote work under `OPENCODE_CLUSTER_ROOT`
- Does not run `rm`, `rmdir`, `mv`, overwrite, or terminate processes without explicit confirmation
- Never creates or interrupts screen sessions automatically
- Stops and asks when remote configuration is incomplete

**Example:** `cluster/job "run tests and deploy"`

---

### cluster/pull

**Description:** Download a file or folder from the configured remote host.

**Behavior:**
- Loads `cluster-ssh` and `cluster-scp`
- Parses the first token as a path relative to `OPENCODE_CLUSTER_ROOT`
- Verifies it remotely
- Downloads it to the matching local relative path
- Does not delete an existing local target without confirmation

**Example:** `cluster/pull logs/output.log`

---

### cluster/push

**Description:** Upload a local file or folder to the configured remote host.

**Behavior:**
- Loads `cluster-scp`
- If no path is supplied, stops with `no target specified, usage: cluster.push <local-path>`
- Parses the first token as the local path
- Mirrors it below `OPENCODE_CLUSTER_ROOT` by default
- If the user explicitly says `root`, uploads its contents to the remote root
- Verifies the local path and remote parent before transferring

**Example:** `cluster/push config/settings.yaml`

---

### cluster/run

**Description:** Run a script or command on the configured remote host.

**Behavior:**
- Loads `cluster-ssh`
- Verifies `OPENCODE_CLUSTER_USER`, `OPENCODE_CLUSTER_HOST`, and `OPENCODE_CLUSTER_ROOT`
- Changes to the configured root
- Activates the configured virtualenv if present
- Runs only the command explicitly provided by the user
- Uses an existing configured screen session for long-running work

**Example:** `cluster/run "python manage.py migrate"`

---

### cluster/update-packages

**Description:** Inspect and synchronize dependencies on a configured remote project.

**Behavior:**
- Loads `cluster-ssh`, `cluster-scp`, and `package-management`
- Detects the active repository's dependency manifests and package manager
- Does not assume `requirements.txt` or Python
- Shows proposed local and remote changes before installing anything
- Does not modify a remote environment without explicit user approval

**Example:** `cluster/update-packages`

---

## Remote-Root Containment

All remote operations must stay below configured remote root:
- `/home/user/project/` (POSIX)
- `C:\Users\user\project\` (Windows)

## Destructive Commands

### Classification

Destructive remote commands include:
- `rm -rf`
- `chmod -R`
- `chown -R`
- `find -delete`
- `git push --force`
- `git reset --hard`

### Approval Requirements

Before executing destructive commands:
1. Show command to execute
2. Show target path
3. Show potential impact
4. Require explicit approval

## Error Handling

### Common Errors

1. **Connection failed**: Check remote connectivity
2. **Authentication failed**: Verify credentials
3. **Permission denied**: Check file permissions
4. **Timeout**: Increase timeout or simplify command
5. **Output exceeded**: Reduce output or increase limit

### Recovery

1. Log error details
2. Provide actionable message
3. Suggest recovery steps
4. Report partial success

## Best Practices

1. **Preview before mutation**: Show changes before applying
2. **Require confirmation**: For all mutations
3. **Use argument arrays**: Prefer over shell strings when possible
4. **Bound output**: Prevent unbounded capture
5. **Classify destructive**: Require approval for dangerous operations
