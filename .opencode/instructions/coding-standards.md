# Coding Standards

- Follow the active repository's existing language and framework conventions.
- Use descriptive names and explicit control flow over compressed one-liners.
- Keep functions focused and preserve established public interfaces unless the
  task explicitly changes them.
- Add type annotations where the language supports them and where the project
  convention expects them.
- Handle invalid input at the boundary when the project has an established error
  model; otherwise preserve its existing failure behavior rather than inventing a
  new one.
- Keep imports, formatting, tests, and dependency changes consistent with the
  active repository.
