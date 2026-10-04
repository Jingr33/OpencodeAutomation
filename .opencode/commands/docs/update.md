---
description: Create or update documentation for a repository path
agent: docs
subtask: true
---

Update documentation for the active repository using the single optional path
argument after the command: `$ARGUMENTS`. If no argument is supplied, use `all`
and review the whole repository. Otherwise treat the complete argument as one
repository-relative file or directory path, such as `src/processors` or
`src/main.py`.

1. Inspect repository instructions first, including `AGENTS.md`, contribution
   guidance, and any documentation-specific requirements. Identify the
   repository's documentation roots, style, navigation, and generated or
   ignored paths before editing.
2. Validate the requested scope. `all` means the complete source tree; a file
   means that file; a directory means every relevant file below it. Do not
   follow paths outside the repository, and do not modify source code for this
   command. Exclude dependency, VCS, build, cache, and generated directories
   unless repository instructions explicitly require documenting them.
3. Read the scoped code and its related tests, configuration, and public
   interfaces. Compare them with the existing documentation and update only
   claims, examples, links, API descriptions, and navigation that are stale.
   Every new statement must be supported by the current repository contents;
   do not guess architecture or behavior.
4. Prefer the repository's existing documentation location and structure. If
   no documentation exists, create `docs/` and add focused Markdown pages for
   the requested scope, including an appropriate entry point when useful. Do
   not duplicate an accurate page merely because the scope was selected.
5. Check internal links, command examples, filenames, and code identifiers
   against the current tree. Run relevant existing documentation, link, lint,
   or test checks when available, and report checks that do not exist or could
   not be run.

Finish with a concise report of the resolved scope, files changed, verification
performed, and any documentation gaps that remain.
