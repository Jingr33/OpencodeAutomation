# Worktree Management System

This document describes the worktree management system for the OpenCode Automation repository.

## Overview

The worktree system allows concurrent work on multiple tasks by creating isolated Git worktrees. Each worktree has its own working directory and branch, enabling parallel development without conflicts.

## Directory Structure

```
.worktrees/
├── BLOBS_project/                      # repository checkout
├── feature-1-github-issue-templates/   # task worktree (first level)
├── feature-2-initialize-opencode-repo/ # task worktree (first level)
└── ...
```

Every checkout — repository clones and task worktrees alike — lives directly under the worktree root at the first level. The worktree root is `.worktrees/` by default, or a custom location specified by `OPENCODE_WORKTREE_ROOT`. Branch names are sanitized to flat directory names (e.g., `feature/1-github-issue-templates` becomes `feature-1-github-issue-templates`).

Worktrees are never nested. A worktree is never created inside another worktree or inside a repository checkout, so `.worktrees/<repo>/.worktrees/<branch>` is forbidden and rejected by the helper. When the repository checkout itself lives under `.worktrees/`, new worktrees are first-level siblings of that checkout.

## Permissions

Created worktrees and repository clones are opened up to every local account. On Windows the helper grants `Everyone` full control recursively with inheritance (`icacls /grant *S-1-1-0:(OI)(CI)F /T`, using the language-independent SID); on POSIX systems it applies `chmod -R a+rwX`. When the worktree root itself is created, the same inheritable access is applied to the root. If granting fails, creation continues and prints a warning.

## Commands

### Create a Worktree

```bash
python .opencode/scripts/worktree.py create <branch> [base] [--repo <path>] [--path <path>]
```

**Arguments:**
- `branch`: Name of the new branch
- `base`: Base branch to create from (defaults to repository's default branch)
- `--repo`: Registered repository checkout to create the worktree from; never a task worktree
- `--root`: Worktree root; defaults to `OPENCODE_WORKTREE_ROOT` or the framework `.worktrees/` directory when the repository checkout lives under it
- `--path`: Custom worktree location; must stay at the first level under the worktree root

**Behavior:**
- If the branch already exists, attaches to the existing worktree
- Creates a new branch from the base if the branch doesn't exist
- Places the worktree directly under the worktree root as a first-level sibling of the repository checkout
- Refuses destinations nested inside another worktree
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
- Exits immediately for dirty worktrees unless `--force` is provided
- `--force` only for explicitly approved dirty worktrees
- Prunes stale Git worktree metadata after removal

### Cleanup Worktrees

```bash
python .opencode/scripts/worktree.py cleanup --closed-prs [--repo <path>] [--apply] [--force]
```

**Behavior:**
1. Preview candidates first (without `--apply`)
2. Check dirty state and closed PR status
3. Exits immediately for dirty worktrees unless `--force` is provided
4. Use `--force` only for explicitly approved dirty worktrees
5. When `--closed-prs` is used, also preview and remove inactive local branches
   whose pull request was merged into the default branch and whose local tip is
   at or behind its remote (or last known PR) copy

Local branches currently checked out, attached to an unsafe worktree, or newer
than their remote copy are never removed.

## Integration with VS Code

Add worktrees to VS Code workspace (requires `workspace.py` script):

```bash
python .opencode/scripts/workspace.py add <worktree-path> --name <slug>
```

Note: The `workspace.py` script is part of the workspace integration feature and may not be available in all branches.

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
