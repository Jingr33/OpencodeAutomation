# Worktree Management System

This document describes the worktree management system for the OpenCode Automation repository.

## Overview

The worktree system allows concurrent work on multiple tasks by creating isolated Git worktrees. Each worktree has its own working directory and branch, enabling parallel development without conflicts.

## Directory Structure

```
.worktrees/
├── feature/1-github-issue-templates/
├── feature/2-initialize-opencode-repo/
├── feature/3-coding-standards/
└── ...
```

Worktrees are stored in `.worktrees/` by default, or in a custom location specified by `OPENCODE_WORKTREE_ROOT`.

## Commands

### Create a Worktree

```bash
python .opencode/scripts/worktree.py create <branch> [base] [--repo <path>] [--path <path>]
```

**Arguments:**
- `branch`: Name of the new branch
- `base`: Base branch to create from (defaults to repository's default branch)
- `--repo`: Repository path (defaults to current directory)
- `--path`: Custom worktree location

**Behavior:**
- If the branch already exists, attaches to the existing worktree
- Creates a new branch from the base if the branch doesn't exist
- Reports the worktree path and branch

### List Worktrees

```bash
python .opencode/scripts/worktree.py list [--repo <path>]
```

**Output:**
```json
[
  {
    "path": "/path/to/worktree",
    "branch": "feature/1-github-issue-templates",
    "dirty": false
  }
]
```

### Remove a Worktree

```bash
python .opencode/scripts/worktree.py remove <path-or-branch> --repo <path> [--force]
```

**Safety Rules:**
- Never removes the main worktree
- Requires explicit confirmation for dirty worktrees
- `--force` only for explicitly approved dirty worktrees
- Prunes stale Git worktree metadata after removal

### Cleanup Worktrees

```bash
python .opencode/scripts/worktree.py cleanup --closed-prs [--repo <path>] [--apply] [--force]
```

**Behavior:**
1. Preview candidates first (without `--apply`)
2. Check dirty state and closed PR status
3. Only remove after user confirmation
4. Use `--force` only for explicitly approved dirty worktrees

## Integration with VS Code

Add worktrees to VS Code workspace:

```bash
python .opencode/scripts/workspace.py add <worktree-path> --name <slug>
```

## Best Practices

1. **One worktree per task**: Create a separate worktree for each concurrent task
2. **Clean before cleanup**: Ensure worktrees are clean before removal
3. **Review candidates**: Always preview cleanup candidates before applying
4. **Use descriptive branch names**: Follow the pattern `<type>/<number>-<slug>`
5. **Document changes**: Update documentation when modifying worktree behavior

## Troubleshooting

### Worktree creation fails
- Check if the branch already exists
- Verify the base branch exists
- Ensure sufficient disk space

### Cannot remove worktree
- Check if the worktree is dirty
- Verify you're not trying to remove the main worktree
- Use `--force` only when explicitly confirmed

### Cleanup doesn't find candidates
- Ensure `gh` CLI is installed and authenticated
- Check if PRs are actually closed
- Verify the worktree is managed (not external)
