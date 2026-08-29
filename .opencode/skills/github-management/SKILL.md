---
name: github-management
description: Handles generic GitHub pull request comments, reviews, and review-thread resolution
license: MIT
compatibility: opencode
---

Resolve the repository from the active checkout or `OPENCODE_GITHUB_REPO`.
Use `gh pr list --head <branch> --json number,title,url` to locate the pull
request. Review comments are available with:

```bash
gh api repos/<owner>/<repo>/pulls/<number>/comments --paginate
```

Reply to a review comment with the REST replies endpoint. Resolve review threads
with the GraphQL `resolveReviewThread` mutation and the thread ID, not the REST
comment ID. Never assume all comments are actionable: distinguish code fixes,
questions, acknowledgments, and outdated comments, and document skipped comments.
