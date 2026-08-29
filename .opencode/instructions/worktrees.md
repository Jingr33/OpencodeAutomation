# Repository And Worktree Rules

- Worktrees are isolated checkouts of one Git repository, not copies of the
  framework itself. Keep them under `OPENCODE_WORKTREE_ROOT` or the default
  `.worktrees/` directory.
- Each active task gets its own branch and worktree. Do not edit two task branches
  from the same checkout.
- Before reusing a worktree, verify its branch and working tree are clean.
- Cleanup is explicit by default. A worktree whose branch has a closed pull
  request may be considered reusable only after checking its status and removing
  it with the worktree helper.
- Never remove a worktree containing uncommitted changes without explicit user
  confirmation and the `--force` option.
