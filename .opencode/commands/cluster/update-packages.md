---
description: Inspect and synchronize dependencies on a configured Linux cluster project
agent: cluster
subtask: true
---

Load `cluster-ssh`, `cluster-scp`, and `package-management`. Load
`cluster-session` if installation or verification may run for more than a few
minutes.

Follow these steps:

1. Inspect the active repository locally and identify dependency manifests and
   the package manager. Consider files such as `requirements.txt`,
   `pyproject.toml`, `poetry.lock`, `package.json`, `package-lock.json`,
   `environment.yml`, and project-specific manifests. Do not assume Python or
   a particular filename.
2. Determine the requested scope: inspect only, update the local manifest,
   synchronize the remote manifest, install remote dependencies, or verify the
   environment. If the scope is not clear, ask before modifying anything.
3. Compare the local manifest with the configured remote project and inspect
   the configured virtualenv or package environment. Use the package manager's
   read-only commands first. Report missing, extra, and version-mismatched
   packages.
4. Show a proposed plan containing local edits, files to upload, remote
   install commands, expected duration, and whether an existing screen session
   is required. Do not install or edit a manifest before explicit approval.
5. After approval, update the local manifest only as requested, then transfer
   it with `cluster-scp` after verifying the remote parent. Never transfer
   secrets or generated environment files.
6. Activate the configured virtualenv through `cluster-ssh` when applicable.
   Run the package manager's exact synchronization command from the project
   root. For a long install, follow `cluster-session`: use only the configured
   existing idle session and stop if it is missing or busy.
7. Verify the installed versions and run the narrowest import, dependency, or
   project check that proves the update. If verification fails, stop and report
   the partial update; do not roll back automatically.
8. Report manifests inspected, changes made, commands run, package results,
   verification output, and any remaining mismatch.
