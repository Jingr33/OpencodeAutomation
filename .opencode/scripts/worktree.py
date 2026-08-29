"""Create and safely clean concurrent Git worktrees."""

import argparse
import json
import os
import re
import subprocess
from pathlib import Path


def run(command: list[str], cwd: Path, check: bool = True) -> str:
    result = subprocess.run(command, cwd=cwd, check=check, text=True, capture_output=True)
    if check:
        return result.stdout.strip()
    return result.stdout.strip()


def repo_path(args: argparse.Namespace) -> Path:
    return Path(args.repo or os.getcwd()).expanduser().resolve()


def git_common_dir(repo: Path) -> Path | None:
    common = run(["git", "rev-parse", "--git-common-dir"], repo, check=False)
    if not common:
        return None
    common_path = Path(common)
    if not common_path.is_absolute():
        common_path = repo / common_path
    return common_path.resolve()


def is_agentic_repository(repo: Path) -> bool:
    agentic_root = Path(__file__).resolve().parents[2]
    agentic_common_dir = git_common_dir(agentic_root)
    target_common_dir = git_common_dir(repo)
    return agentic_common_dir is not None and agentic_common_dir == target_common_dir


def worktree_root(repo: Path, args: argparse.Namespace) -> Path:
    configured = args.root or os.environ.get("OPENCODE_WORKTREE_ROOT")
    return Path(configured).expanduser().resolve() if configured else repo / ".worktrees"


def branch_path(root: Path, branch: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", branch).strip("-")
    return root / safe


def default_base(repo: Path) -> str:
    head = run(["git", "symbolic-ref", "refs/remotes/origin/HEAD"], repo, check=False)
    if head:
        return head.rsplit("/", 1)[-1]
    remote_info = run(["git", "remote", "show", "origin"], repo, check=False)
    match = re.search(r"^\s*HEAD branch:\s*(\S+)", remote_info, re.MULTILINE)
    if match:
        return match.group(1)
    github_info = subprocess.run(
        ["gh", "repo", "view", "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name"],
        cwd=repo,
        check=False,
        text=True,
        capture_output=True,
    )
    if github_info.returncode == 0 and github_info.stdout.strip():
        return github_info.stdout.strip()
    return run(["git", "branch", "--show-current"], repo)


def worktrees(repo: Path) -> list[dict[str, str | bool]]:
    output = run(["git", "worktree", "list", "--porcelain"], repo)
    records: list[dict[str, str | bool]] = []
    current: dict[str, str | bool] = {}
    for line in output.splitlines() + [""]:
        if line.startswith("worktree "):
            if current:
                records.append(current)
            current = {"path": line[9:]}
        elif line.startswith("branch "):
            current["branch"] = line[7:].removeprefix("refs/heads/")
        elif line == "detached":
            current["branch"] = "(detached)"
        elif not line and current:
            records.append(current)
            current = {}
    unique: dict[str, dict[str, str | bool]] = {}
    for record in records:
        path = Path(str(record["path"]))
        record["dirty"] = bool(run(["git", "status", "--porcelain"], path, check=False)) if path.exists() else False
        unique[str(path)] = record
    return list(unique.values())


def create(args: argparse.Namespace) -> None:
    repo = repo_path(args)
    if is_agentic_repository(repo):
        raise SystemExit(
            "refusing to create a worktree for the agentic repository; "
            "implement it in the current checkout"
        )
    branch = args.branch
    existing = next((item for item in worktrees(repo) if item.get("branch") == branch), None)
    if existing:
        print(json.dumps(existing, indent=2))
        return
    target = Path(args.path).expanduser().resolve() if args.path else branch_path(worktree_root(repo, args), branch)
    target.parent.mkdir(parents=True, exist_ok=True)
    base = args.base or default_base(repo)
    branch_exists = subprocess.run(["git", "show-ref", "--verify", f"refs/heads/{branch}"], cwd=repo, capture_output=True).returncode == 0
    command = ["git", "worktree", "add"]
    if not branch_exists:
        command.extend(["-b", branch, str(target), base])
    else:
        command.extend([str(target), branch])
    run(command, repo)
    print(json.dumps({"path": str(target), "branch": branch, "base": base}, indent=2))


def listing(args: argparse.Namespace) -> None:
    print(json.dumps(worktrees(repo_path(args)), indent=2))


def remove(args: argparse.Namespace) -> None:
    repo = repo_path(args)
    records = worktrees(repo)
    target = next((item for item in records if item.get("path") == str(Path(args.target).expanduser().resolve()) or item.get("branch") == args.target), None)
    if not target:
        raise SystemExit(f"worktree not found: {args.target}")
    if Path(str(target["path"])).resolve() == repo:
        raise SystemExit("refusing to remove the main worktree")
    if target.get("dirty") and not args.force:
        raise SystemExit("worktree is dirty; use --force only after explicit confirmation")
    command = ["git", "worktree", "remove"]
    if args.force:
        command.append("--force")
    command.append(str(target["path"]))
    run(command, repo)
    run(["git", "worktree", "prune"], repo)


def closed_prs(branch: str, repo: Path) -> list[dict[str, str]]:
    command = ["gh", "pr", "list", "--state", "closed", "--head", branch, "--json", "number,url,headRefName", "--limit", "20"]
    result = subprocess.run(command, cwd=repo, text=True, capture_output=True)
    if result.returncode != 0:
        return []
    return json.loads(result.stdout)


def cleanup(args: argparse.Namespace) -> None:
    repo = repo_path(args)
    candidates: list[dict[str, object]] = []
    for item in worktrees(repo):
        branch = str(item.get("branch", ""))
        if not branch or branch == "(detached)" or Path(str(item["path"])).resolve() == repo:
            continue
        prs = closed_prs(branch, repo) if args.closed_prs else []
        if args.closed_prs and not prs:
            continue
        candidates.append({**item, "closed_prs": prs})
    print(json.dumps(candidates, indent=2))
    if not args.apply:
        return
    for candidate in candidates:
        if candidate.get("dirty") and not args.force:
            print(f"skipped dirty worktree: {candidate['path']}")
            continue
        remove_args = argparse.Namespace(repo=str(repo), target=str(candidate["path"]), force=args.force)
        remove(remove_args)


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description=__doc__)
    subparsers = command.add_subparsers(dest="command", required=True)
    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("branch")
    create_parser.add_argument("base", nargs="?")
    create_parser.add_argument("--repo")
    create_parser.add_argument("--root")
    create_parser.add_argument("--path")
    create_parser.set_defaults(function=create)
    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--repo")
    list_parser.add_argument("--root")
    list_parser.set_defaults(function=listing)
    remove_parser = subparsers.add_parser("remove")
    remove_parser.add_argument("target")
    remove_parser.add_argument("--repo")
    remove_parser.add_argument("--root")
    remove_parser.add_argument("--force", action="store_true")
    remove_parser.set_defaults(function=remove)
    cleanup_parser = subparsers.add_parser("cleanup")
    cleanup_parser.add_argument("--repo")
    cleanup_parser.add_argument("--root")
    cleanup_parser.add_argument("--closed-prs", action="store_true")
    cleanup_parser.add_argument("--apply", action="store_true")
    cleanup_parser.add_argument("--force", action="store_true")
    cleanup_parser.set_defaults(function=cleanup)
    return command


if __name__ == "__main__":
    arguments = parser().parse_args()
    arguments.function(arguments)
