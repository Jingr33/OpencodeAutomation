# OpenCode Layout

Commands are grouped by their invocation prefix:

- `dev.*`: implementation, builds, documentation, reviews, and startup.
- `issue.*`: GitHub Issue lifecycle and local issue analysis.
- `repo.*`: external repository registration.
- `worktree.*`: concurrent branch checkout and cleanup.
- `workspace.*`: VS Code multi-root workspace folder management.
- `cluster.*`: configurable SSH/SCP remote work.
- `sync.*`: pull, commit, push, and pull-request workflows.

The agentic repository is always changed in its current checkout. Task
worktrees for external target repositories are added to the VS Code
multi-root workspace automatically by `/issue.create` and `/dev.implement`.

Agents and skills are generic. They inspect the active repository instead of
assuming the source layout from MedSAM or Auto Annotater. Cluster credentials
and paths are supplied through environment variables and are never stored here.
