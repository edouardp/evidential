"""Credential-free local publication receipts and version-specific release notes."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def read_receipt(path: Path) -> dict:
    value = json.loads(path.read_text())
    if (
        not isinstance(value, dict)
        or not isinstance(value.get("version"), str)
        or not isinstance(value.get("commit"), str)
        or not isinstance(value.get("completed"), bool)
    ):
        raise ValueError("Invalid release receipt; inspect local publication state before continuing")
    return value


def write_receipt(path: Path, version: str, commit: str, *, completed: bool = False) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps({"version": version, "commit": commit, "completed": completed}) + "\n")
    temporary.replace(path)


def check_pending(path: Path) -> None:
    if path.exists() and not read_receipt(path)["completed"]:
        version = read_receipt(path)["version"]
        raise ValueError(
            f"Publication already succeeded. Run make release-resume VERSION={version} before a new release"
        )


def check_publish(path: Path, version: str) -> None:
    check_pending(path)
    if path.exists() and read_receipt(path)["version"] == version:
        raise ValueError(f"Version {version} was already published; use release-resume instead of uploading again")


def verify_receipt(path: Path, version: str, commit: str) -> str:
    if not path.exists():
        raise ValueError("No successful-upload receipt; verify PyPI manually before recovering this release")
    receipt = read_receipt(path)
    if (receipt["version"], receipt["commit"]) != (version, commit):
        raise ValueError("Release version/HEAD does not match the published receipt; refusing to tag another commit")
    return "prerelease" if re.search(r"(?:a|b|rc)\d+$", version) else "stable"


def release_notes(changelog: str, version: str) -> str:
    match = re.search(rf"^## {re.escape(version)} \([^\n]*\)\s*\n(.*?)(?=^## |\Z)", changelog, re.MULTILINE | re.DOTALL)
    if not match or not match.group(1).strip():
        raise ValueError(f"No release notes for {version}")
    return match.group(1).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["pending", "publish", "record", "verify", "complete", "notes"])
    parser.add_argument("path", type=Path)
    parser.add_argument("version", nargs="?", default="")
    parser.add_argument("commit", nargs="?", default="")
    args = parser.parse_args()
    try:
        if args.action == "pending":
            check_pending(args.path)
        elif args.action == "publish":
            check_publish(args.path, args.version)
        elif args.action == "record":
            write_receipt(args.path, args.version, args.commit)
        elif args.action == "verify":
            print(verify_receipt(args.path, args.version, args.commit))
        elif args.action == "complete":
            verify_receipt(args.path, args.version, args.commit)
            write_receipt(args.path, args.version, args.commit, completed=True)
        else:
            print(release_notes(args.path.read_text(), args.version), end="")
    except (ValueError, OSError) as error:
        parser.exit(1, f"ERROR: {error}\n")


if __name__ == "__main__":
    main()
