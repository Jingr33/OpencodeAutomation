# OpencodeAutomation

Reusable OpenCode infrastructure for developing several repositories and branches
from one workspace.

## What is included

- Namespaced commands for development, GitHub Issues, reviews, synchronization,
  remote cluster work, repositories, and worktrees.
- GitHub Issue and optional GitHub Project workflows without a hard-coded owner,
  repository, or project number.
- Repository registration and cloning through `repo.*` commands.
- Isolated concurrent branches through `worktree.*` commands.
- Automatic worktree cleanup based on closed pull requests, with explicit
  confirmation before destructive operations.

## Quick start

1. Open this repository in OpenCode.
2. Add a target repository with `/repo.add <url>` or work directly in this repo.
3. Create an isolated branch with `/worktree.create <branch> [base-branch]`.
4. Use `/dev.implement <issue-number>` for implementation and `/issue.*` for
   GitHub Issue management.

The repository and worktree locations can be changed with `OPENCODE_REPO_ROOT`
and `OPENCODE_WORKTREE_ROOT`. Cluster commands are configured only through
`OPENCODE_CLUSTER_*` environment variables; no credentials are stored here.
