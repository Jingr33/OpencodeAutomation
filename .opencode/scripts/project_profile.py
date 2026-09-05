"""Project profile schema and validation for OpenCode Automation."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# Project profile schema version
SCHEMA_VERSION = 1


def validate_profile(profile: dict[str, Any]) -> list[str]:
    """
    Validate a project profile against the schema.
    
    Args:
        profile: Project profile dictionary
    
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Check required fields
    if "version" not in profile:
        errors.append("Missing required field: version")
    elif profile["version"] != SCHEMA_VERSION:
        errors.append(f"Unsupported schema version: {profile['version']} (expected {SCHEMA_VERSION})")
    
    if "projectType" not in profile:
        errors.append("Missing required field: projectType")
    elif profile["projectType"] not in ["react", "node", "python", "dotnet", "godot", "generic"]:
        errors.append(f"Invalid projectType: {profile['projectType']}")
    
    if "root" not in profile:
        errors.append("Missing required field: root")
    elif not isinstance(profile["root"], str):
        errors.append("Field 'root' must be a string")
    
    # Validate services
    if "services" in profile:
        if not isinstance(profile["services"], list):
            errors.append("Field 'services' must be a list")
        else:
            for i, service in enumerate(profile["services"]):
                if not isinstance(service, dict):
                    errors.append(f"Service {i} must be a dictionary")
                    continue
                
                if "id" not in service:
                    errors.append(f"Service {i} missing required field: id")
                
                if "command" in service:
                    if not isinstance(service["command"], list):
                        errors.append(f"Service {i} 'command' must be a list")
                
                if "readiness" in service:
                    readiness = service["readiness"]
                    if not isinstance(readiness, dict):
                        errors.append(f"Service {i} 'readiness' must be a dictionary")
                    elif "type" not in readiness:
                        errors.append(f"Service {i} 'readiness' missing required field: type")
                    elif readiness["type"] not in ["http", "tcp", "process", "file"]:
                        errors.append(f"Service {i} 'readiness' invalid type: {readiness['type']}")
    
    # Validate checks
    if "checks" in profile:
        if not isinstance(profile["checks"], dict):
            errors.append("Field 'checks' must be a dictionary")
        else:
            for check_type, command in profile["checks"].items():
                if check_type not in ["build", "test", "lint", "format"]:
                    errors.append(f"Invalid check type: {check_type}")
                elif not isinstance(command, list):
                    errors.append(f"Check '{check_type}' command must be a list")
    
    # Validate packageManager
    if "packageManager" in profile:
        valid_managers = ["npm", "yarn", "pnpm", "bun", "pip", "poetry", "uv", "dotnet", "cargo", "go"]
        if profile["packageManager"] not in valid_managers:
            errors.append(f"Invalid packageManager: {profile['packageManager']}")
    
    # Validate environment
    if "environment" in profile:
        if not isinstance(profile["environment"], dict):
            errors.append("Field 'environment' must be a dictionary")
    
    # Validate ports
    if "ports" in profile:
        if not isinstance(profile["ports"], list):
            errors.append("Field 'ports' must be a list")
        else:
            for i, port in enumerate(profile["ports"]):
                if not isinstance(port, dict):
                    errors.append(f"Port {i} must be a dictionary")
                elif "number" not in port:
                    errors.append(f"Port {i} missing required field: number")
                elif not isinstance(port["number"], int) or port["number"] < 1 or port["number"] > 65535:
                    errors.append(f"Port {i} 'number' must be an integer between 1 and 65535")
    
    # Validate shutdown
    if "shutdown" in profile:
        if not isinstance(profile["shutdown"], dict):
            errors.append("Field 'shutdown' must be a dictionary")
        elif "command" in profile["shutdown"]:
            if not isinstance(profile["shutdown"]["command"], list):
                errors.append("Field 'shutdown.command' must be a list")
    
    # Validate documentation
    if "documentation" in profile:
        if not isinstance(profile["documentation"], dict):
            errors.append("Field 'documentation' must be a dictionary")
        else:
            for key, value in profile["documentation"].items():
                if key not in ["roots", "readme"]:
                    errors.append(f"Invalid documentation field: {key}")
    
    return errors


def load_profile(path: Path) -> dict[str, Any] | None:
    """Load a project profile from a file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing profile: {e}", file=sys.stderr)
        return None


def validate_profile_file(path: Path) -> bool:
    """Validate a project profile file."""
    profile = load_profile(path)
    if profile is None:
        return False
    
    errors = validate_profile(profile)
    if errors:
        print(f"Validation errors in {path}:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return False
    
    print(f"Profile {path} is valid")
    return True


def create_example_profile() -> dict[str, Any]:
    """Create an example project profile."""
    return {
        "version": SCHEMA_VERSION,
        "projectType": "react",
        "root": ".",
        "packageManager": "pnpm",
        "services": [
            {
                "id": "web",
                "cwd": ".",
                "command": ["pnpm", "dev"],
                "readiness": {
                    "type": "http",
                    "url": "http://127.0.0.1:3000",
                    "timeoutSeconds": 60
                }
            }
        ],
        "checks": {
            "build": ["pnpm", "build"],
            "test": ["pnpm", "test"],
            "lint": ["pnpm", "lint"]
        },
        "environment": {
            "NODE_ENV": "development"
        },
        "ports": [
            {
                "number": 3000,
                "protocol": "tcp",
                "description": "Development server"
            }
        ],
        "shutdown": {
            "command": ["pkill", "-f", "pnpm dev"],
            "timeoutSeconds": 10
        },
        "documentation": {
            "roots": ["docs"],
            "readme": "README.md"
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Project profile schema and validation")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a project profile")
    validate_parser.add_argument("path", help="Path to opencode.project.json")
    
    # Example command
    example_parser = subparsers.add_parser("example", help="Show example project profile")
    
    args = parser.parse_args()
    
    if args.command == "validate":
        path = Path(args.path)
        if not path.exists():
            print(f"File not found: {path}", file=sys.stderr)
            sys.exit(1)
        
        success = validate_profile_file(path)
        sys.exit(0 if success else 1)
    
    elif args.command == "example":
        print(json.dumps(create_example_profile(), indent=2))


if __name__ == "__main__":
    main()
