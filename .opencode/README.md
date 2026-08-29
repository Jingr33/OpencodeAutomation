# OpenCode Layout

Commands are grouped by their invocation prefix:

- `dev.*`: implementation, builds, documentation, reviews, and startup.
- `issue.*`: GitHub Issue lifecycle and local issue analysis.
- `repo.*`: external repository registration.
- `worktree.*`: concurrent branch checkout and cleanup.
- `cluster.*`: configurable SSH/SCP remote work.
- `sync.*`: pull, commit, push, and pull-request workflows.

Agents and skills are generic. They inspect the active repository instead of
assuming the source layout from MedSAM or Auto Annotater. Cluster credentials
and paths are supplied through environment variables and are never stored here.
