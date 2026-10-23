---
description: Clone a remote repository and open it in a fresh worktree without starting a task
subtask: true
---

Load the `repository` and `worktree` skills. Parse `$ARGUMENTS` as
`<url-or-owner/name>`, with optional `--name <name>` and `--branch <branch>`.

1. Reject a remote URL that embeds credentials; never store them in a remote
   URL.
2. Clone and register the repository with
   `python .opencode/scripts/repository.py add <url-or-owner/name> [--name <name>]`
   and take the clone path from its JSON output. An already existing clone is
   reused instead of being cloned again.
3. After cloning, verify the new repository before continuing:
   - Confirm `<clone-path>` is an initialized Git repository with
     `git -C <clone-path> rev-parse --is-inside-work-tree`. If the check fails,
     initialize it with `git -C <clone-path> init`.
   - Confirm `origin` points at the repository the user specified with
     `git -C <clone-path> remote get-url origin`. If `origin` is missing, add
     it with `git -C <clone-path> remote add origin <repo-url>`; if it points
     at a different repository, correct it with
     `git -C <clone-path> remote set-url origin <repo-url>`. `<repo-url>` is
     the resolved clone URL of `<url-or-owner/name>`. Never embed credentials
     in the URL.
   - If the repository was initialized locally instead of cloned, download its
     content from the specified remote with `git -C <clone-path> fetch origin`
     and check out the remote's default branch, so the working tree comes from
     that remote repository.
4. Create a fresh worktree of that clone with
   `python .opencode/scripts/worktree.py create <branch> --repo <clone-path>`.
   Let the helper resolve the repository's actual default branch as the base
   and place the worktree under `OPENCODE_WORKTREE_ROOT` or `.worktrees/`.
   Default `<branch>` to `clone/<repo-name>`, where `<repo-name>` is the name
   registered in step 2. If a worktree for that branch already exists, reuse it
   instead of creating a duplicate branch.
5. Report the clone path, worktree path, branch, and base, then stop. Do not
   fetch Issues, implement anything, commit, or push.
