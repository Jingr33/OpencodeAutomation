# Repository And Worktree Rules

- Worktrees are isolated checkouts of a target Git repository, not copies of the
  framework itself. Keep them under `OPENCODE_WORKTREE_ROOT` or the default
  `.worktrees/` directory.
- Each active task for an external or managed target gets its own branch and
  worktree. Do not edit two task branches from the same checkout.
- Before creating a new worktree, check whether an existing clean worktree
  already serves the same branch. If it does, reuse it rather than creating a
  duplicate. Verify its branch and working tree are clean before reuse.
- The agentic repository containing this automation configuration is a strict
  exception: implement its Issues and configuration changes in the current
  checkout and current branch. Never create, select, or switch to another
  worktree for it. The worktree helper must refuse such a request.
- Issue creation (`/issue.create`) must not create branches or worktrees. Branch
  and worktree creation is the responsibility of the dev and CR commands that
  operate on the Issue later.
- Cleanup is explicit by default. A worktree whose branch has a closed pull
  request may be considered reusable only after checking its status and removing
  it with the worktree helper.
- Never remove a worktree containing uncommitted changes without explicit user
  confirmation and the `--force` option.
