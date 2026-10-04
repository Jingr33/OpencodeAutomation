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

**Description:** Execute a user-described multi-step job on a configured Linux
cluster safely.

**Workflow:**
1. Parse the user's description into local preparation, transfers, remote
   commands, and downloads.
2. Stop and ask when a path, operation, execution mode, or destructive impact
   is ambiguous.
3. Show the planned order, path mappings, remote root, and direct-versus-screen
   mode.
4. Validate `OPENCODE_CLUSTER_*` settings and the remote root.
5. Transfer with `cluster-scp`, execute with `cluster-ssh`, and verify each
   dependent step before continuing.
6. Use `cluster-session` for long-running work; require the configured existing
   idle screen session and stop if it is missing or busy.
7. Report completed steps, partial results, failures, and skipped steps.

**Example:** `cluster/job "run tests and deploy"`

---

### cluster/pull

**Description:** Download a file or folder from a configured Linux cluster.

**Workflow:**
1. Parse the first argument as a remote-relative path and recognize
   `files-only` as a direct-files-only option.
2. Reject root escapes, validate cluster configuration, and verify the remote
   source before downloading.
3. Map the source to the same local relative path and check the local parent.
4. Request confirmation before overwriting or merging into an existing target.
5. In `files-only` mode, list direct regular files and transfer each one;
   never recurse into subdirectories.
6. Retry one failed transfer, verify the local result, and report partial
   completion.

**Example:** `cluster/pull logs/output.log`

---

### cluster/push

**Description:** Upload a local file or folder to a configured Linux cluster.

**Workflow:**
1. Parse the first argument as the local source and recognize only explicit
   `root` mode as a mapping override.
2. Verify the local source and reject paths outside the active repository unless
   explicitly confirmed.
3. Map the source to the remote root, show the mapping, and check for an
   existing target.
4. Request confirmation before overwriting remote data.
5. Verify the remote parent, transfer recursively with one retry, and verify the
   result without deleting or moving remote data.

**Example:** `cluster/push config/settings.yaml`

---

### cluster/push-src

**Description:** Upload a local directory's contents to a configured Linux
cluster root.

**Workflow:**
1. Use the supplied local directory or `src` when no argument is supplied.
2. Verify the local directory and cluster configuration, then verify the remote
   root.
3. Show the root-mode mapping and request confirmation before overwriting.
4. Transfer contents directly below the remote root, preserving subdirectories;
   do not add an extra source-directory level.
5. Verify the result, retrying one failed transfer, and report partial state.

**Example:** `cluster/push-src src`

---

### cluster/run

**Description:** Run an explicit command on a configured Linux cluster.

**Workflow:**
1. Preserve the complete argument string as the requested command; do not add
   flags or cleanup.
2. Validate the cluster configuration and remote root.
3. Activate the configured virtualenv only after verifying its relative path.
4. Run short read-only commands directly; use `cluster-session` for explicit or
   inferred long-running work.
5. For screen work, verify the configured existing session is present and idle;
   never create, detach, interrupt, or kill it.
6. Capture bounded direct output or the last observed screen output and report
   the mode, result, command, and root.

**Example:** `cluster/run "python manage.py migrate"`

---

### cluster/update-packages

**Description:** Inspect and synchronize dependencies on a configured Linux
cluster project.

**Workflow:**
1. Detect local dependency manifests and the package manager instead of assuming
   Python or `requirements.txt`.
2. Determine whether the user requested inspection, manifest changes, remote
   synchronization, installation, or verification.
3. Compare local and remote state with read-only checks and show a proposed
   mutation plan before editing or installing.
4. After approval, update and transfer only the requested manifests.
5. Activate the configured virtualenv when applicable and run the exact package
   manager synchronization command from the remote root.
6. Use `cluster-session` for long installations and stop when the configured
   session is missing or busy.
7. Verify versions or imports and report all changes, output, and partial state.

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
