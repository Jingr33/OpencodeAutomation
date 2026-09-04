# Synchronization and Cluster Operations

This document defines the split synchronization commands and cluster operation behavior.

## Synchronization Commands

### sync/commit

**Syntax:**
```
sync/commit [--message <message>] [--all] [--repo <path>]
```

**Arguments:**
- `--message`: Commit message (required)
- `--all`: Stage all changes
- `--repo`: Target repository path

**Preconditions:**
- Changes exist to commit
- Working directory is not clean
- Commit message is provided

**Preview:**
- Show files to be committed
- Show commit message
- Show branch and repository

**Confirmation:**
- Required before commit

**Output:**
```json
{
  "command": "sync/commit",
  "status": "succeeded",
  "commit": "abc123",
  "files": ["file1.cs", "file2.cs"],
  "message": "Add feature X"
}
```

### sync/push

**Syntax:**
```
sync/push [--repo <path>] [--force]
```

**Arguments:**
- `--repo`: Target repository path
- `--force`: Force push (requires confirmation)

**Preconditions:**
- Commits exist to push
- Remote is configured
- Authentication is available

**Preview:**
- Show commits to push
- Show remote and branch
- Show force push warning (if applicable)

**Confirmation:**
- Required before push
- Extra confirmation for force push

**Output:**
```json
{
  "command": "sync/push",
  "status": "succeeded",
  "remote": "origin",
  "branch": "feature/my-feature",
  "commits": 3
}
```

### sync/pr

**Syntax:**
```
sync/pr [--title <title>] [--body <body>] [--base <branch>] [--repo <path>]
```

**Arguments:**
- `--title`: PR title (required)
- `--body`: PR body
- `--base`: Base branch (default: main)
- `--repo`: Target repository path

**Preconditions:**
- Branch has commits
- No existing PR for branch
- Remote is configured

**Preview:**
- Show PR title and body
- Show base and head branches
- Show files changed

**Confirmation:**
- Required before PR creation

**Output:**
```json
{
  "command": "sync/pr",
  "status": "succeeded",
  "pr": 123,
  "url": "https://github.com/org/repo/pull/123",
  "title": "Add feature X"
}
```

### sync/ship

**Syntax:**
```
sync/ship [--message <message>] [--repo <path>]
```

**Arguments:**
- `--message`: Commit message (required)
- `--repo`: Target repository path

**Preconditions:**
- Changes exist
- Remote is configured
- Authentication is available

**Preview:**
- Show commit message
- Show files to be committed
- Show push details
- Show PR creation details

**Confirmation:**
- Required before ship

**Orchestration:**
1. Commit changes
2. Push to remote
3. Create or update PR
4. Report results

**Output:**
```json
{
  "command": "sync/ship",
  "status": "succeeded",
  "commit": "abc123",
  "pr": 123,
  "url": "https://github.com/org/repo/pull/123"
}
```

## Cluster Operations

### Command Execution

#### Argument-Array Mode

```bash
# Preferred: argument array
["ls", "-la", "/path/to/directory"]
```

#### Shell Mode

```bash
# Only when shell syntax is required
shell: "ls -la /path/to/directory | grep .txt"
```

### Remote-Root Containment

All remote operations must stay below configured remote root:
- `/home/user/project/` (POSIX)
- `C:\Users\user\project\` (Windows)

### Symlink Policy

- Follow symlinks within remote root
- Reject symlinks outside remote root
- Report symlink targets in preview

### Timeout and Cancellation

- Default timeout: 300 seconds
- Configurable per command
- Support cancellation via signal

### Output Capture

- Capture stdout and stderr
- Bound output size (1MB default)
- Preserve timeout context

### Retries

- Default retries: 3
- Exponential backoff
- Configurable per command

### Overwrite Rules

- Never overwrite without `--force`
- Preview before overwrite
- Require confirmation for destructive overwrites

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

1. **Use argument arrays**: Prefer over shell strings
2. **Preview before mutation**: Show changes before applying
3. **Require confirmation**: For all mutations
4. **Bound output**: Prevent unbounded capture
5. **Classify destructive**: Require approval for dangerous operations
