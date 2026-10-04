"""Resolve, prepare, and run Python projects with their declared toolchain."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from urllib.parse import urlparse
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:  # pragma: no cover - Python 3.10 fallback
    tomllib = None

from command_runner import run_command
from process_manager import start_process, stop_process, get_process_status


MANAGERS = {"pip", "uv", "poetry", "pipenv"}
PYTHON_COMMANDS = {"python", "python3", "py"}
MANAGER_COMMANDS = {"uv", "poetry", "pipenv"}


class PythonRuntimeError(RuntimeError):
    """Raised when a Python project cannot be resolved safely."""


def _load_toml(path: Path) -> dict[str, Any]:
    if tomllib is None:
        return {}
    try:
        with path.open("rb") as file:
            value = tomllib.load(file)
        return value if isinstance(value, dict) else {}
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def _load_profile(project_root: Path) -> tuple[dict[str, Any] | None, str | None]:
    path = project_root / "opencode.project.json"
    if not path.exists():
        return None, None
    try:
        with path.open("r", encoding="utf-8") as file:
            profile = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise PythonRuntimeError(f"Cannot read {path}: {error}") from error
    if not isinstance(profile, dict):
        raise PythonRuntimeError(f"Profile {path} must contain a JSON object")
    return profile, str(path)


def _profile_root(project_root: Path, profile: dict[str, Any] | None) -> Path:
    relative_root = profile.get("root", ".") if profile else "."
    if not isinstance(relative_root, str):
        raise PythonRuntimeError("Profile field 'root' must be a string")
    root = (project_root / relative_root).resolve()
    if not root.exists() or not root.is_dir():
        raise PythonRuntimeError(f"Configured Python root does not exist: {root}")
    return root


def _python_markers(project_root: Path) -> list[str]:
    markers = []
    for name in (
        "pyproject.toml",
        "uv.lock",
        "poetry.lock",
        "Pipfile",
        "Pipfile.lock",
        "requirements.txt",
        "requirements-dev.txt",
    ):
        if (project_root / name).exists():
            markers.append(f"{name} found")
    return markers


def _detect_manager(project_root: Path, profile: dict[str, Any] | None) -> tuple[str, list[str]]:
    evidence: list[str] = []
    profile_python = profile.get("python", {}) if profile else {}
    if not isinstance(profile_python, dict):
        raise PythonRuntimeError("Profile field 'python' must be an object")

    explicit = profile_python.get("manager") or (profile or {}).get("packageManager")
    if explicit is not None:
        if explicit not in MANAGERS:
            raise PythonRuntimeError(
                f"Unsupported Python package manager '{explicit}'. Use one of: {', '.join(sorted(MANAGERS))}"
            )
        evidence.append(f"package manager explicitly configured: {explicit}")
        return explicit, evidence

    if (project_root / "uv.lock").exists():
        return "uv", ["uv.lock found"]
    if (project_root / "poetry.lock").exists():
        return "poetry", ["poetry.lock found"]
    if (project_root / "Pipfile.lock").exists() or (project_root / "Pipfile").exists():
        return "pipenv", ["Pipfile/Pipfile.lock found"]

    pyproject = _load_toml(project_root / "pyproject.toml")
    if "uv" in pyproject.get("tool", {}):
        return "uv", ["[tool.uv] found in pyproject.toml"]
    if "poetry" in pyproject.get("tool", {}):
        return "poetry", ["[tool.poetry] found in pyproject.toml"]
    if (project_root / "requirements.txt").exists() or list(project_root.glob("requirements-*.txt")):
        return "pip", ["requirements file found"]
    if (project_root / "pyproject.toml").exists():
        return "pip", ["pyproject.toml found; using venv and pip"]

    raise PythonRuntimeError(
        "No supported Python dependency declaration found. Expected uv.lock, "
        "poetry.lock, Pipfile, requirements*.txt, or pyproject.toml."
    )


def _environment_dir(project_root: Path, profile: dict[str, Any] | None, manager: str) -> Path:
    profile_python = profile.get("python", {}) if profile else {}
    if not isinstance(profile_python, dict):
        profile_python = {}
    configured = profile_python.get("environment") or (profile or {}).get("pythonEnvironment")
    if configured is not None and not isinstance(configured, str):
        raise PythonRuntimeError("Python environment path must be a string")
    if configured:
        return (project_root / configured).resolve()
    if manager == "uv":
        return (project_root / ".venv").resolve()
    if manager == "pip":
        if (project_root / ".venv").exists() or not (project_root / "venv").exists():
            return (project_root / ".venv").resolve()
        return (project_root / "venv").resolve()
    return (project_root / ".venv").resolve()


def _python_executable(environment: Path) -> Path:
    relative = Path("Scripts/python.exe") if os.name == "nt" else Path("bin/python")
    return environment / relative


def _declared_scripts(project_root: Path) -> list[str]:
    pyproject = _load_toml(project_root / "pyproject.toml")
    project = pyproject.get("project", {})
    tool = pyproject.get("tool", {})
    scripts: dict[str, Any] = {}
    if isinstance(project, dict) and isinstance(project.get("scripts"), dict):
        scripts.update(project["scripts"])
    if isinstance(project, dict) and isinstance(project.get("gui-scripts"), dict):
        scripts.update(project["gui-scripts"])
    poetry = tool.get("poetry", {}) if isinstance(tool, dict) else {}
    if isinstance(poetry, dict) and isinstance(poetry.get("scripts"), dict):
        scripts.update(poetry["scripts"])
    return sorted(str(name) for name in scripts)


def _select_service(profile: dict[str, Any] | None, service_id: str | None) -> dict[str, Any] | None:
    services = profile.get("services", []) if profile else []
    if not isinstance(services, list):
        raise PythonRuntimeError("Profile field 'services' must be a list")
    python_services = [service for service in services if isinstance(service, dict)]
    if service_id:
        matches = [service for service in python_services if service.get("id") == service_id]
        if len(matches) != 1:
            raise PythonRuntimeError(f"Python service '{service_id}' was not found in the project profile")
        return matches[0]
    if len(python_services) == 1:
        return python_services[0]
    if len(python_services) > 1:
        names = ", ".join(str(service.get("id", "<unnamed>")) for service in python_services)
        raise PythonRuntimeError(f"Multiple Python services found ({names}); pass --service")
    return None


def _select_command(
    project_root: Path,
    profile: dict[str, Any] | None,
    service_id: str | None,
    entrypoint: str | None,
) -> tuple[list[str] | None, dict[str, Any] | None, list[str]]:
    evidence: list[str] = []
    service = _select_service(profile, service_id)
    if service is not None:
        command = service.get("command")
        if not isinstance(command, list) or not command or not all(isinstance(item, str) for item in command):
            raise PythonRuntimeError("Selected service must define a non-empty string command list")
        evidence.append(f"service '{service.get('id', service_id)}' command from opencode.project.json")
        return list(command), service, evidence

    configured = None
    if profile:
        configured = profile.get("run")
        python_config = profile.get("python", {})
        if isinstance(python_config, dict) and python_config.get("run") is not None:
            configured = python_config["run"]
    if configured is not None:
        if not isinstance(configured, list) or not configured or not all(isinstance(item, str) for item in configured):
            raise PythonRuntimeError("Configured Python run command must be a non-empty string list")
        evidence.append("run command from opencode.project.json")
        return list(configured), None, evidence

    scripts = _declared_scripts(project_root)
    if entrypoint:
        if entrypoint not in scripts:
            raise PythonRuntimeError(
                f"Entrypoint '{entrypoint}' is not declared in pyproject.toml. Available: {', '.join(scripts) or 'none'}"
            )
        evidence.append(f"declared project script selected: {entrypoint}")
        return [entrypoint], None, evidence
    if len(scripts) == 1:
        evidence.append(f"single declared project script selected: {scripts[0]}")
        return [scripts[0]], None, evidence
    if len(scripts) > 1:
        raise PythonRuntimeError(
            "Multiple Python entrypoints are declared; pass --entrypoint or define a service in opencode.project.json: "
            + ", ".join(scripts)
        )
    return None, None, ["no declared Python entrypoint found"]


def _creation_python(profile: dict[str, Any] | None) -> str:
    python_config = profile.get("python", {}) if profile else {}
    configured = python_config.get("executable") if isinstance(python_config, dict) else None
    configured = configured or (profile or {}).get("pythonExecutable")
    if configured is not None:
        if not isinstance(configured, str) or not configured:
            raise PythonRuntimeError("Configured Python executable must be a non-empty string")
        return configured
    return sys.executable


def _prepare_commands(
    project_root: Path,
    manager: str,
    environment: Path,
    profile: dict[str, Any] | None,
) -> list[list[str]]:
    if manager == "uv":
        return [["uv", "sync", "--locked"] if (project_root / "uv.lock").exists() else ["uv", "sync"]]
    if manager == "poetry":
        return [["poetry", "install"]]
    if manager == "pipenv":
        return [["pipenv", "sync"] if (project_root / "Pipfile.lock").exists() else ["pipenv", "install"]]

    commands: list[list[str]] = []
    python = str(_python_executable(environment))
    if not _python_executable(environment).exists():
        commands.append([_creation_python(profile), "-m", "venv", str(environment)])
    python_config = profile.get("python", {}) if profile else {}
    configured_requirements = python_config.get("requirements") if isinstance(python_config, dict) else None
    if configured_requirements is not None:
        if not isinstance(configured_requirements, str) or not configured_requirements:
            raise PythonRuntimeError("Configured Python requirements path must be a non-empty string")
        requirements = (project_root / configured_requirements).resolve()
        if not requirements.exists():
            raise PythonRuntimeError(f"Configured requirements file does not exist: {requirements}")
    else:
        requirements = project_root / "requirements.txt"
    if requirements.exists():
        commands.append([python, "-m", "pip", "install", "-r", str(requirements)])
    elif (project_root / "pyproject.toml").exists():
        commands.append([python, "-m", "pip", "install", "-e", str(project_root)])
    else:
        requirement_files = sorted(project_root.glob("requirements-*.txt"))
        if len(requirement_files) > 1:
            raise PythonRuntimeError(
                "Multiple requirements files found without requirements.txt; "
                "declare the dependency file in opencode.project.json"
            )
        if requirement_files:
            commands.append([python, "-m", "pip", "install", "-r", str(requirement_files[0])])
    return commands


def _wrapped_command(manager: str, command: list[str], environment: Path) -> list[str]:
    if not command:
        raise PythonRuntimeError("Cannot run an empty Python command")
    first = Path(command[0]).name.lower()
    if first in MANAGER_COMMANDS:
        return command
    if first in PYTHON_COMMANDS and manager != "pip":
        return [manager, "run", *command]
    if manager == "uv":
        return ["uv", "run", *command]
    if manager == "poetry":
        return ["poetry", "run", *command]
    if manager == "pipenv":
        return ["pipenv", "run", *command]
    if first in PYTHON_COMMANDS:
        return [str(_python_executable(environment)), *command[1:]]
    return command


def _environment(project_root: Path, manager: str, environment: Path, profile: dict[str, Any] | None) -> dict[str, str]:
    result = os.environ.copy()
    configured = profile.get("environment", {}) if profile else {}
    if isinstance(configured, dict):
        result.update({str(key): str(value) for key, value in configured.items()})
    if manager == "pip":
        result["VIRTUAL_ENV"] = str(environment)
        bin_dir = environment / ("Scripts" if os.name == "nt" else "bin")
        result["PATH"] = str(bin_dir) + os.pathsep + result.get("PATH", "")
    return result


def _safe_process_id(project_root: Path, service_id: str | None) -> str:
    digest = hashlib.sha1(str(project_root).encode("utf-8")).hexdigest()[:8]
    name = service_id or "app"
    safe_name = "".join(character if character.isalnum() or character in "-_" else "-" for character in name)
    return f"python-{safe_name}-{digest}"


def _normalize_readiness(root: Path, service: dict[str, Any] | None) -> dict[str, Any] | None:
    readiness = service.get("readiness") if service else None
    if readiness is None:
        return None
    if not isinstance(readiness, dict):
        raise PythonRuntimeError("Service readiness must be an object")
    readiness = dict(readiness)
    readiness_type = readiness.get("type")
    if readiness_type not in {"http", "tcp", "file", "process"}:
        raise PythonRuntimeError("Readiness type must be http, tcp, file, or process")
    if readiness_type == "http" and not isinstance(readiness.get("url"), str):
        raise PythonRuntimeError("HTTP readiness requires a URL")
    if readiness_type == "tcp" and not isinstance(readiness.get("port"), int):
        raise PythonRuntimeError("TCP readiness requires an integer port")
    if readiness_type == "file":
        path = readiness.get("path")
        if not isinstance(path, str):
            raise PythonRuntimeError("File readiness requires a path")
        if not Path(path).is_absolute():
            readiness["path"] = str(root / path)
    if "timeoutSeconds" in readiness and (
        not isinstance(readiness["timeoutSeconds"], int) or readiness["timeoutSeconds"] <= 0
    ):
        raise PythonRuntimeError("Readiness timeoutSeconds must be a positive integer")
    return readiness


def resolve_python_project(
    project_root: Path,
    service_id: str | None = None,
    entrypoint: str | None = None,
) -> dict[str, Any]:
    """Resolve a Python project without changing files or installing packages."""
    project_root = project_root.resolve()
    profile, profile_source = _load_profile(project_root)
    root = _profile_root(project_root, profile)
    manager, manager_evidence = _detect_manager(root, profile)
    environment = _environment_dir(root, profile, manager)
    command, service, command_evidence = _select_command(root, profile, service_id, entrypoint)
    wrapped = _wrapped_command(manager, command, environment) if command else None
    profile_env = _environment(root, manager, environment, profile)
    safe_env = {
        "VIRTUAL_ENV": profile_env.get("VIRTUAL_ENV", ""),
        "PATH_PREFIX": str(environment / ("Scripts" if os.name == "nt" else "bin")) if manager == "pip" else "",
    }
    readiness = _normalize_readiness(root, service)
    return {
        "projectType": "python",
        "root": str(root),
        "source": profile_source or "technology_detection",
        "packageManager": manager,
        "environment": str(environment),
        "python": str(_python_executable(environment)),
        "managerAvailable": shutil.which(manager) is not None if manager != "pip" else True,
        "evidence": _python_markers(root) + manager_evidence + command_evidence,
        "prepare": _prepare_commands(root, manager, environment, profile),
        "command": wrapped,
        "rawCommand": command,
        "readiness": readiness,
        "environmentSummary": safe_env,
        "profileEnvironment": str(project_root / "opencode.project.json") if profile else None,
        "processId": _safe_process_id(root, service_id or (service or {}).get("id")),
        "checks": profile.get("checks", {}) if profile else {},
    }


def detect_python_project(project_root: Path) -> dict[str, Any]:
    """Detect Python dependency management without selecting an entrypoint."""
    project_root = project_root.resolve()
    profile, profile_source = _load_profile(project_root)
    root = _profile_root(project_root, profile)
    manager, manager_evidence = _detect_manager(root, profile)
    environment = _environment_dir(root, profile, manager)
    return {
        "source": profile_source or "technology_detection",
        "packageManager": manager,
        "environment": str(environment),
        "evidence": _python_markers(root) + manager_evidence,
    }


def prepare_project(resolution: dict[str, Any]) -> dict[str, Any]:
    """Install or synchronize dependencies according to the resolved manager."""
    root = Path(resolution["root"])
    environment = Path(resolution["environment"])
    manager = resolution["packageManager"]
    commands = [list(command) for command in resolution["prepare"]]
    results = []
    for command in commands:
        result = run_command(
            command,
            cwd=root,
            env=_environment_for_resolution(resolution),
            timeout=1800,
        )
        results.append(result)
        if result["exitCode"] != 0:
            return {"success": False, "commands": results, "error": result.get("error") or result["stderr"]}
    if manager == "pip" and not _python_executable(environment).exists():
        return {"success": False, "commands": results, "error": f"Python environment was not created: {environment}"}
    return {"success": True, "commands": results}


def run_project(resolution: dict[str, Any], prepare: bool = True) -> dict[str, Any]:
    if not resolution.get("command"):
        raise PythonRuntimeError(
            "No Python entrypoint is declared. Add opencode.project.json with 'run' or a service command."
        )
    preparation = prepare_project(resolution) if prepare else {"success": True, "skipped": True}
    if not preparation["success"]:
        return {"success": False, "preparation": preparation}
    readiness = resolution.get("readiness")
    port = None
    if isinstance(readiness, dict):
        if isinstance(readiness.get("port"), int):
            port = readiness["port"]
        elif isinstance(readiness.get("url"), str):
            try:
                parsed = urlparse(readiness["url"])
                port = parsed.port
            except ValueError as error:
                raise PythonRuntimeError(f"Invalid readiness URL: {error}") from error
    process = start_process(
        resolution["processId"],
        resolution["command"],
        Path(resolution["root"]),
        env=_environment_for_resolution(resolution),
        port=port,
        readiness=readiness,
        timeout=int((readiness or {}).get("timeoutSeconds", 30)),
    )
    return {"success": process.get("success", False), "preparation": preparation, "process": process}


def _environment_for_resolution(resolution: dict[str, Any]) -> dict[str, str]:
    result = os.environ.copy()
    profile_path = resolution.get("profileEnvironment")
    if profile_path:
        profile, _ = _load_profile(Path(profile_path).parent)
        configured = profile.get("environment", {}) if profile else {}
        if isinstance(configured, dict):
            result.update({str(key): str(value) for key, value in configured.items()})
    if resolution["packageManager"] == "pip":
        environment = Path(resolution["environment"])
        result["VIRTUAL_ENV"] = str(environment)
        bin_dir = environment / ("Scripts" if os.name == "nt" else "bin")
        result["PATH"] = str(bin_dir) + os.pathsep + result.get("PATH", "")
    elif resolution["packageManager"] == "uv":
        result["UV_PROJECT_ENVIRONMENT"] = resolution["environment"]
    return result


def _print_result(result: dict[str, Any]) -> int:
    print(json.dumps(result, indent=2, default=str))
    return 0 if result.get("success", True) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve and run a Python project with its declared toolchain")
    subparsers = parser.add_subparsers(dest="action", required=True)
    for name in ("plan", "prepare", "run"):
        action = subparsers.add_parser(name)
        action.add_argument("--project-root", default=".")
        action.add_argument("--service")
        action.add_argument("--entrypoint")
        action.add_argument("--no-prepare", action="store_true")
    for name in ("status", "stop"):
        action = subparsers.add_parser(name)
        action.add_argument("--project-root", default=".")
        action.add_argument("--service")
        action.add_argument("--entrypoint")
        if name == "stop":
            action.add_argument("--force", action="store_true")
    check = subparsers.add_parser("check")
    check.add_argument("name", choices=["build", "test", "lint", "format"])
    check.add_argument("--project-root", default=".")
    check.add_argument("--no-prepare", action="store_true")

    args = parser.parse_args()
    try:
        root = Path(args.project_root)
        if args.action == "check":
            resolution = resolve_python_project(root)
            checks = resolution.get("checks", {})
            command = checks.get(args.name)
            if not isinstance(command, list) or not command:
                raise PythonRuntimeError(f"No '{args.name}' check is declared in the project profile")
            resolution["command"] = _wrapped_command(
                resolution["packageManager"], command, Path(resolution["environment"])
            )
            preparation = prepare_project(resolution) if not args.no_prepare else {"success": True, "skipped": True}
            if not preparation["success"]:
                return _print_result({"success": False, "preparation": preparation})
            check_result = run_command(
                resolution["command"],
                cwd=Path(resolution["root"]),
                env=_environment_for_resolution(resolution),
                timeout=1800,
            )
            return _print_result({
                "success": check_result["exitCode"] == 0,
                "preparation": preparation,
                "check": check_result,
            })

        resolution = resolve_python_project(root, args.service, args.entrypoint)
        if args.action == "plan":
            return _print_result({"success": True, "plan": resolution})
        if args.action == "prepare":
            return _print_result({"success": True, "plan": resolution, "preparation": prepare_project(resolution)})
        if args.action == "run":
            return _print_result(run_project(resolution, prepare=not args.no_prepare))
        if args.action == "status":
            return _print_result(get_process_status(resolution["processId"]))
        if args.action == "stop":
            return _print_result(stop_process(resolution["processId"], force=args.force))
    except PythonRuntimeError as error:
        return _print_result({"success": False, "error": str(error)})
    except (OSError, subprocess.SubprocessError) as error:
        return _print_result({"success": False, "error": str(error)})
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
