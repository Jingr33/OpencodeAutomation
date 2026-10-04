"""Tests for local branch cleanup during worktree cleanup."""

import subprocess
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent / ".opencode" / "scripts"))

import worktree


def git(repo: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=repo,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def repository_with_branch(tmp_path: Path) -> tuple[Path, str]:
    git(tmp_path, "init", "-b", "main")
    git(tmp_path, "config", "user.email", "tests@example.invalid")
    git(tmp_path, "config", "user.name", "Tests")
    (tmp_path / "README.md").write_text("initial\n", encoding="utf-8")
    git(tmp_path, "add", "README.md")
    git(tmp_path, "commit", "-m", "initial")
    commit = git(tmp_path, "rev-parse", "HEAD")
    git(tmp_path, "branch", "feature/merged")
    return tmp_path, commit


def test_merged_branch_at_remote_tip_is_obsolete(monkeypatch, tmp_path):
    repo, commit = repository_with_branch(tmp_path)
    monkeypatch.setattr(worktree, "default_base", lambda _repo: "main")
    monkeypatch.setattr(
        worktree,
        "merged_prs",
        lambda _branch, _repo: [{"number": 1, "baseRefName": "main", "headRefOid": commit}],
    )

    candidates = worktree.obsolete_local_branches(repo)

    assert [candidate["branch"] for candidate in candidates] == ["feature/merged"]


def test_branch_with_newer_local_commit_is_preserved(monkeypatch, tmp_path):
    repo, commit = repository_with_branch(tmp_path)
    git(repo, "switch", "feature/merged")
    (repo / "README.md").write_text("local work\n", encoding="utf-8")
    git(repo, "add", "README.md")
    git(repo, "commit", "-m", "local work")
    git(repo, "switch", "main")
    monkeypatch.setattr(worktree, "default_base", lambda _repo: "main")
    monkeypatch.setattr(
        worktree,
        "merged_prs",
        lambda _branch, _repo: [{"number": 1, "baseRefName": "main", "headRefOid": commit}],
    )

    assert worktree.obsolete_local_branches(repo) == []
