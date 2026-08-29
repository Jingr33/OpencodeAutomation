# GitHub Integration

GitHub commands must derive the repository from the active checkout whenever
possible. Use `gh repo view --json nameWithOwner` or `git remote get-url origin`
instead of hard-coded owner/repository values.

Optional configuration:

- `OPENCODE_GITHUB_REPO`: explicit `owner/name` override.
- `OPENCODE_GITHUB_PROJECT`: numeric project number.
- `OPENCODE_GITHUB_PROJECT_OWNER`: project owner; defaults to the repository owner.

Project status updates are optional. If no project is configured, manage the
Issue and report that project synchronization was skipped. Never put credentials
in command files or Git remotes.
