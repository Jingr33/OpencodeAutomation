---
name: worktree
description: Creates, lists, reuses, and safely cleans concurrent Git worktrees
license: MIT
compatibility: opencode
---

# Worktree Management Skill

## Step 1 - Understand the Worktree System

The worktree system manages concurrent Git worktrees for parallel development. Worktrees are stored outside the main checkout by default.

## Step 2 - Create a Worktree

To create a new worktree:

1. Run the worktree creation command
2. Specify the branch name
3. Optionally specify the base branch
4. The system will create the worktree at the appropriate location

**Command:**
```bash
python .opencode/scripts/worktree.py create <branch> [base]
```

**Options:**
- `--repo <path>`: Repository path
- `--root <path>`: Custom worktree root
- `--path <path>`: Custom worktree location

## Step 3 - List Worktrees

To list all existing worktrees:

1. Run the worktree list command
2. Review the output showing paths, branches, and status

**Command:**
```bash
python .opencode/scripts/worktree.py list [--repo <path>]
```

## Step 4 - Remove a Worktree

To remove a worktree safely:

1. Identify the worktree to remove
2. Verify it's not the main worktree
3. Check if it's dirty (use `--force` only with explicit confirmation)
4. Run the removal command

**Command:**
```bash
python .opencode/scripts/worktree.py remove <path-or-branch> [--repo <path>] [--force]
```

**Safety Rules:**
- Never remove the main worktree
- Require explicit confirmation for dirty worktrees
- Use `--force` only when explicitly approved

## Step 5 - Cleanup Worktrees

To clean up worktrees with closed PRs:

1. Preview candidates first
2. Check dirty state and closed PR status
3. Only remove after user confirmation
4. Use `--force` only for explicitly approved dirty worktrees

**Commands:**
```bash
# Preview candidates
python .opencode/scripts/worktree.py cleanup --closed-prs [--repo <path>]

# Apply cleanup
python .opencode/scripts/worktree.py cleanup --closed-prs --apply [--force]
```

## Step 6 - Integrate with VS Code

To add a worktree to VS Code workspace:

1. Get the worktree path
2. Run the workspace add command
3. Provide a descriptive name

**Command:**
```bash
python .opencode/scripts/workspace.py add <worktree-path> --name <slug>
```

## Important Notes

- Worktrees are isolated checkouts, not copies
- Each task gets its own branch and worktree
- Verify branch and working tree are clean before reuse
- Cleanup is explicit by default
- Never remove a worktree with uncommitted changes without confirmation
