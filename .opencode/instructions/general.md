# General Rules

- Inspect the active repository before making assumptions about its layout,
  language, package manager, default branch, or deployment environment.
- Do only the work requested by the user. Preserve unrelated working-tree changes.
- Do not commit secrets, tokens, passwords, generated dependencies, or private
  machine details.
- Prefer small, reversible changes. Run the narrowest relevant verification after
  editing.
- Shared automation must be generic. Repository-specific behavior belongs in the
  target repository or in explicit local configuration.
