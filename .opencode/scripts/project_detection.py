"""Deterministic project profile detection for OpenCode Automation."""

import argparse
import json
import re
from pathlib import Path
from typing import Any


def detect_package_manager(project_root: Path) -> dict[str, Any]:
    """Detect package manager from lockfiles."""
    evidence = []
    
    # Check for lockfiles in order
    if (project_root / "pnpm-lock.yaml").exists():
        evidence.append("pnpm-lock.yaml found")
        return {"packageManager": "pnpm", "evidence": evidence}
    
    if (project_root / "yarn.lock").exists():
        evidence.append("yarn.lock found")
        return {"packageManager": "yarn", "evidence": evidence}
    
    if (project_root / "package-lock.json").exists():
        evidence.append("package-lock.json found")
        return {"packageManager": "npm", "evidence": evidence}
    
    if (project_root / "bun.lock").exists():
        evidence.append("bun.lock found")
        return {"packageManager": "bun", "evidence": evidence}
    
    # Check for Python package managers
    if (project_root / "uv.lock").exists():
        evidence.append("uv.lock found")
        return {"packageManager": "uv", "evidence": evidence}
    
    if (project_root / "poetry.lock").exists():
        evidence.append("poetry.lock found")
        return {"packageManager": "poetry", "evidence": evidence}
    
    if (project_root / "Pipfile.lock").exists():
        evidence.append("Pipfile.lock found")
        return {"packageManager": "pipenv", "evidence": evidence}
    
    # Check for .NET
    if list(project_root.glob("*.sln")):
        evidence.append("Solution file found")
        return {"packageManager": "dotnet", "evidence": evidence}
    
    # Check for Rust
    if (project_root / "Cargo.lock").exists():
        evidence.append("Cargo.lock found")
        return {"packageManager": "cargo", "evidence": evidence}
    
    # Check for Go
    if (project_root / "go.sum").exists():
        evidence.append("go.sum found")
        return {"packageManager": "go", "evidence": evidence}
    
    return {"packageManager": None, "evidence": ["No lockfiles found"]}


def detect_project_type(project_root: Path, package_manager: str | None) -> dict[str, Any]:
    """Detect project type from manifests and dependencies."""
    evidence = []
    project_type = None
    
    # Check for package.json (Node.js/React)
    package_json_path = project_root / "package.json"
    if package_json_path.exists():
        try:
            with open(package_json_path, "r", encoding="utf-8") as f:
                package_json = json.load(f)
            
            dependencies = package_json.get("dependencies", {})
            dev_dependencies = package_json.get("devDependencies", {})
            all_deps = {**dependencies, **dev_dependencies}
            
            # Check for React
            if "react" in all_deps or "react-dom" in all_deps:
                evidence.append("React dependency found in package.json")
                project_type = "react"
            else:
                evidence.append("Node.js project (no React dependency)")
                project_type = "node"
            
            # Check scripts
            scripts = package_json.get("scripts", {})
            if "dev" in scripts:
                evidence.append(f"dev script found: {scripts['dev']}")
            if "start" in scripts:
                evidence.append(f"start script found: {scripts['start']}")
            if "build" in scripts:
                evidence.append(f"build script found: {scripts['build']}")
            if "test" in scripts:
                evidence.append(f"test script found: {scripts['test']}")
        
        except (json.JSONDecodeError, KeyError) as e:
            evidence.append(f"Error parsing package.json: {e}")
    
    # Check for Python
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.exists():
        evidence.append("pyproject.toml found")
        project_type = "python"
    
    requirements_path = project_root / "requirements.txt"
    if requirements_path.exists():
        evidence.append("requirements.txt found")
        project_type = "python"
    
    # Check for .NET
    if list(project_root.glob("*.csproj")):
        evidence.append("C# project file found")
        project_type = "dotnet"
    
    # Check for GODOT
    godot_path = project_root / "project.godot"
    if godot_path.exists():
        evidence.append("GODOT project file found")
        project_type = "godot"
    
    return {"projectType": project_type, "evidence": evidence}


def detect_services(project_root: Path, project_type: str | None) -> list[dict[str, Any]]:
    """Detect services based on project type."""
    services = []
    evidence = []
    
    if project_type in ["react", "node"]:
        package_json_path = project_root / "package.json"
        if package_json_path.exists():
            try:
                with open(package_json_path, "r", encoding="utf-8") as f:
                    package_json = json.load(f)
                
                scripts = package_json.get("scripts", {})
                
                # Detect dev server
                if "dev" in scripts:
                    services.append({
                        "id": "dev",
                        "command": ["npm", "run", "dev"],
                        "evidence": [f"dev script: {scripts['dev']}"]
                    })
                elif "start" in scripts:
                    services.append({
                        "id": "start",
                        "command": ["npm", "start"],
                        "evidence": [f"start script: {scripts['start']}"]
                    })
                
                # Detect build
                if "build" in scripts:
                    services.append({
                        "id": "build",
                        "command": ["npm", "run", "build"],
                        "evidence": [f"build script: {scripts['build']}"]
                    })
            
            except (json.JSONDecodeError, KeyError):
                pass
    
    return services


def detect_checks(project_root: Path, project_type: str | None) -> dict[str, list[str]]:
    """Detect build/test/lint commands."""
    checks = {}
    evidence = []
    
    if project_type in ["react", "node"]:
        package_json_path = project_root / "package.json"
        if package_json_path.exists():
            try:
                with open(package_json_path, "r", encoding="utf-8") as f:
                    package_json = json.load(f)
                
                scripts = package_json.get("scripts", {})
                
                if "build" in scripts:
                    checks["build"] = ["npm", "run", "build"]
                    evidence.append(f"build script: {scripts['build']}")
                
                if "test" in scripts:
                    checks["test"] = ["npm", "test"]
                    evidence.append(f"test script: {scripts['test']}")
                
                if "lint" in scripts:
                    checks["lint"] = ["npm", "run", "lint"]
                    evidence.append(f"lint script: {scripts['lint']}")
                
                if "format" in scripts:
                    checks["format"] = ["npm", "run", "format"]
                    evidence.append(f"format script: {scripts['format']}")
            
            except (json.JSONDecodeError, KeyError):
                pass
    
    return checks


def detect_project(project_root: Path) -> dict[str, Any]:
    """
    Detect project configuration following the documented precedence.
    
    Precedence:
    1. opencode.project.json (explicit configuration)
    2. toolkit.startup.md (target repository instructions)
    3. AGENTS.md Startup section (target repository instructions)
    4. Technology-specific detection rules
    """
    evidence = []
    detection_source = None
    
    # 1. Check for explicit opencode.project.json
    profile_path = project_root / "opencode.project.json"
    if profile_path.exists():
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                profile = json.load(f)
            evidence.append(f"Explicit profile found at {profile_path}")
            return {
                "source": "opencode.project.json",
                "profile": profile,
                "evidence": evidence
            }
        except (json.JSONDecodeError, KeyError) as e:
            evidence.append(f"Error parsing opencode.project.json: {e}")
    
    # 2. Check for toolkit.startup.md
    startup_md_path = project_root / "toolkit.startup.md"
    if startup_md_path.exists():
        evidence.append(f"toolkit.startup.md found at {startup_md_path}")
        # Parse startup instructions from markdown
        # For now, return basic detection
    
    # 3. Check for AGENTS.md Startup section
    agents_md_path = project_root / "AGENTS.md"
    if agents_md_path.exists():
        try:
            with open(agents_md_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Look for Startup section
            startup_match = re.search(r'##\s*Startup\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
            if startup_match:
                evidence.append(f"AGENTS.md Startup section found")
                # Parse startup instructions from markdown
        except Exception:
            pass
    
    # 4. Technology-specific detection
    package_manager = detect_package_manager(project_root)
    project_type = detect_project_type(project_root, package_manager.get("packageManager"))
    services = detect_services(project_root, project_type.get("projectType"))
    checks = detect_checks(project_root, project_type.get("projectType"))
    
    evidence.extend(package_manager.get("evidence", []))
    evidence.extend(project_type.get("evidence", []))
    
    profile = {
        "version": 1,
        "projectType": project_type.get("projectType"),
        "root": ".",
        "packageManager": package_manager.get("packageManager"),
        "services": services,
        "checks": checks
    }
    
    return {
        "source": "technology_detection",
        "profile": profile,
        "evidence": evidence
    }


def main():
    parser = argparse.ArgumentParser(description="Deterministic project profile detection")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument("--output", choices=["json", "text"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    project_root = Path(args.project_root) if args.project_root else Path.cwd()
    
    if not project_root.exists():
        print(f"Project root does not exist: {project_root}")
        return 1
    
    result = detect_project(project_root)
    
    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Detection Source: {result['source']}")
        print(f"Project Type: {result['profile'].get('projectType', 'unknown')}")
        print(f"Package Manager: {result['profile'].get('packageManager', 'unknown')}")
        print(f"\nEvidence:")
        for e in result['evidence']:
            print(f"  - {e}")
    
    return 0


if __name__ == "__main__":
    exit(main())
