"""Run SSH/SCP clients with credentials read from Windows Credential Manager.

The helper keeps credential lookup out of prompts, command files, and logs. It
is intentionally a small transport wrapper: SSH keys and agents remain the
preferred authentication method, while Windows users can opt into a stored
generic credential for PuTTY's ``plink`` and ``pscp`` clients.
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes
import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Sequence


class CredentialError(RuntimeError):
    """Raised when the configured Windows credential cannot be read."""


@dataclass(frozen=True)
class Credential:
    """The non-secret identity and secret returned by Credential Manager."""

    username: str
    secret: str


if os.name == "nt":

    class _Credential(ctypes.Structure):
        _fields_ = [
            ("Flags", ctypes.wintypes.DWORD),
            ("Type", ctypes.wintypes.DWORD),
            ("TargetName", ctypes.wintypes.LPWSTR),
            ("Comment", ctypes.wintypes.LPWSTR),
            ("LastWritten", ctypes.wintypes.FILETIME),
            ("CredentialBlobSize", ctypes.wintypes.DWORD),
            ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
            ("Persist", ctypes.wintypes.DWORD),
            ("AttributeCount", ctypes.wintypes.DWORD),
            ("Attributes", ctypes.c_void_p),
            ("TargetAlias", ctypes.wintypes.LPWSTR),
            ("UserName", ctypes.wintypes.LPWSTR),
        ]


def _decode_secret(blob: bytes) -> str:
    """Decode a stored generic credential without exposing it in errors."""

    encodings = (
        ("utf-16-le", "utf-8")
        if b"\x00" in blob
        else ("utf-8", "utf-16-le")
    )
    for encoding in encodings:
        try:
            secret = blob.decode(encoding).rstrip("\x00")
        except UnicodeDecodeError:
            continue
        if secret:
            return secret
    raise CredentialError("configured Windows credential has an invalid secret")


def read_windows_credential(target: str) -> Credential:
    """Read a generic credential from Windows Credential Manager."""

    if os.name != "nt":
        raise CredentialError(
            "Windows Credential Manager is available only on Windows; use an SSH key or agent"
        )
    if not target or any(character in target for character in "\r\n\x00"):
        raise CredentialError("OPENCODE_CLUSTER_CREDENTIAL_TARGET is invalid")

    credential_pointer = ctypes.POINTER(_Credential)()
    advapi32 = ctypes.WinDLL("Advapi32.dll")
    read = advapi32.CredReadW
    read.argtypes = [
        ctypes.wintypes.LPWSTR,
        ctypes.wintypes.DWORD,
        ctypes.wintypes.DWORD,
        ctypes.POINTER(ctypes.POINTER(_Credential)),
    ]
    read.restype = ctypes.wintypes.BOOL
    free = advapi32.CredFree
    free.argtypes = [ctypes.c_void_p]
    free.restype = None

    # CRED_TYPE_GENERIC is 1. Keep this value local so the helper has no
    # dependency on a Windows SDK or third-party package.
    if not read(target, 1, 0, ctypes.byref(credential_pointer)):
        raise CredentialError("configured Windows credential was not found")

    try:
        record = credential_pointer.contents
        if not record.UserName or not record.CredentialBlob:
            raise CredentialError("configured Windows credential is incomplete")
        blob = ctypes.string_at(record.CredentialBlob, record.CredentialBlobSize)
        return Credential(record.UserName, _decode_secret(blob))
    finally:
        free(credential_pointer)


def _client_command(transport: str, configured: str | None) -> list[str]:
    """Resolve a transport executable without invoking a shell."""

    target = os.environ.get("OPENCODE_CLUSTER_CREDENTIAL_TARGET", "")
    default = {
        "ssh": "plink" if target else "ssh",
        "scp": "pscp" if target else "scp",
    }[transport]
    command = shlex.split(configured or default, posix=False)
    if not command:
        raise CredentialError(f"OPENCODE_CLUSTER_{transport.upper()}_CLIENT is empty")
    if shutil.which(command[0]) is None and not os.path.isfile(command[0]):
        raise CredentialError(f"cluster {transport} client is not available")
    return command


def run_transport(transport: str, arguments: Sequence[str]) -> int:
    """Run the configured SSH or SCP client and return its exit code."""

    if not arguments:
        raise CredentialError(f"cluster {transport} requires a destination")

    target = os.environ.get("OPENCODE_CLUSTER_CREDENTIAL_TARGET", "")
    configured = os.environ.get(f"OPENCODE_CLUSTER_{transport.upper()}_CLIENT")
    if not configured and transport == "ssh":
        # Preserve the original configuration name for existing users.
        configured = os.environ.get("OPENCODE_CLUSTER_SSH_COMMAND")
    command = _client_command(transport, configured)

    if target:
        executable_name = os.path.splitext(os.path.basename(command[0]))[0].lower()
        expected_client = "plink" if transport == "ssh" else "pscp"
        if executable_name != expected_client:
            raise CredentialError(
                "Windows Credential Manager password authentication requires "
                f"{expected_client}; configure the corresponding cluster client"
            )
        credential = read_windows_credential(target)
        # plink/pscp accept the password only as a process argument. The
        # wrapper obtains it at runtime and never prints, stores, or logs it.
        command.extend(["-batch", "-l", credential.username, "-pw", credential.secret])
    command.extend(arguments)
    completed = subprocess.run(command, check=False)
    return completed.returncode


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transport", choices=("ssh", "scp"))
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the selected transport while keeping secrets out of output."""

    parsed = _parser().parse_args(argv)
    arguments = list(parsed.arguments)
    if arguments and arguments[0] == "--":
        arguments.pop(0)
    try:
        return run_transport(parsed.transport, arguments)
    except CredentialError as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
