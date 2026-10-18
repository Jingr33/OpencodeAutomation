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

1. Resolve the registered repository checkout with
   `python .opencode/scripts/repository.py list` (or read
   `.opencode/state/repositories.json`). Pass its exact path as `--repo`; it is
   the repository's main clone even when it lives under `.worktrees/`.
2. Run the worktree creation command with the branch name and optional base.
3. The worktree MUST be created directly under the worktree root at the first
   level: `<worktree-root>/<sanitized-branch>`, a sibling of the repository
   checkout. Never pass a task worktree as `--repo` and never nest a worktree
   inside another worktree or a repository checkout.
4. Verify the printed worktree path is a direct child of `OPENCODE_WORKTREE_ROOT`
   or `.worktrees/` before reporting it. Nested paths such as
   `.worktrees/<repo>/.worktrees/<branch>` are forbidden and are rejected by the
   helper.

**Command:**
```bash
python .opencode/scripts/worktree.py create <branch> --repo <registered-checkout> [base]
```

**Options:**
- `--repo <path>`: Registered repository checkout, never a task worktree
- `--root <path>`: Worktree root; defaults to `OPENCODE_WORKTREE_ROOT` or the
  framework `.worktrees/` directory
- `--path <path>`: Explicit destination; it must stay at the first level under
  the worktree root and never inside another worktree

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
- Created worktrees are accessible to every local account: the helper grants
  `Everyone` full control recursively on Windows and `a+rwX` on POSIX systems
- All checkouts are first-level children of the worktree root; never nest one
  worktree inside another worktree or inside a repository checkout
- Create worktrees only from the registered repository checkout, never from a
  task worktree
- Each task gets its own branch and worktree
- Verify branch and working tree are clean before reuse
- Cleanup is explicit by default
- Never remove a worktree with uncommitted changes without confirmation
