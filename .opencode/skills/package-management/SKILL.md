---
name: package-management
description: Diagnoses missing, incompatible, and outdated dependencies in any active repository
license: MIT
compatibility: opencode
---

Inspect the repository's dependency manifests and package manager first. Identify
the package name from the error, compare it with the installed environment, and
prefer the project's documented installation workflow. Do not install packages
or rewrite lock files unless the user explicitly requests it. When changes are
requested, update the manifest and lock file using the repository's package
manager and verify imports/builds afterward.
