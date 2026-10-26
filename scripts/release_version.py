#!/usr/bin/env python3
"""Resolve and validate versions for the evidential house release workflow."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from typing import Final

_VERSION_PATTERN: Final = re.compile(
    r"^(?P<major>0|[1-9][0-9]*)\."
    r"(?P<minor>0|[1-9][0-9]*)\."
    r"(?P<patch>0|[1-9][0-9]*)"
    r"(?:(?P<phase>a|b|rc)(?P<serial>0|[1-9][0-9]*))?$"
)
_BUMP_TYPES: Final = frozenset({"patch", "minor", "major"})


class ReleaseVersionError(ValueError):
    """Raised when a release version request is invalid."""


@dataclass(frozen=True)
class ReleaseVersion:
    """A canonical stable or prerelease version accepted by the workflow."""

    major: int
    minor: int
    patch: int
    phase: str | None = None
    serial: int | None = None

    @property
    def is_prerelease(self) -> bool:
        return self.phase is not None

    @property
    def release_kind(self) -> str:
        return "prerelease" if self.is_prerelease else "stable"

    def __str__(self) -> str:
        suffix = "" if self.phase is None else f"{self.phase}{self.serial}"
        return f"{self.major}.{self.minor}.{self.patch}{suffix}"


def parse_version(value: str) -> ReleaseVersion:
    """Parse the deliberately narrow canonical version syntax used for releases."""

    match = _VERSION_PATTERN.fullmatch(value)
    if match is None:
        raise ReleaseVersionError(f"invalid version {value!r}; expected X.Y.Z or X.Y.ZaN, X.Y.ZbN, or X.Y.ZrcN")

    phase = match.group("phase")
    serial = match.group("serial")
    return ReleaseVersion(
        major=int(match.group("major")),
        minor=int(match.group("minor")),
        patch=int(match.group("patch")),
        phase=phase,
        serial=None if serial is None else int(serial),
    )


def resolve_version(current: str, request: str) -> ReleaseVersion:
    """Resolve a conventional bump or validate an exact release version."""

    current_version = parse_version(current)
    if request not in _BUMP_TYPES:
        requested_version = parse_version(request)
        if requested_version == current_version:
            raise ReleaseVersionError(f"requested version {request!r} is already current")
        return requested_version

    if current_version.is_prerelease:
        raise ReleaseVersionError(
            "automatic patch/minor/major bumps require a stable current version; "
            "use --version for prerelease transitions"
        )

    if request == "patch":
        return ReleaseVersion(current_version.major, current_version.minor, current_version.patch + 1)
    if request == "minor":
        return ReleaseVersion(current_version.major, current_version.minor + 1, 0)
    return ReleaseVersion(current_version.major + 1, 0, 0)


def _usage() -> str:
    return "Usage: release_version.py CURRENT <patch|minor|major>\n       release_version.py CURRENT --version VERSION"


def main(argv: list[str] | None = None) -> int:
    """Print ``VERSION RELEASE_KIND`` for consumption by ``release.sh``."""

    args = sys.argv[1:] if argv is None else argv
    if len(args) == 2:
        current, request = args
    elif len(args) == 3 and args[1] == "--version":
        current, _, request = args
    else:
        print(_usage(), file=sys.stderr)
        return 2

    try:
        resolved = resolve_version(current, request)
    except ReleaseVersionError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    print(resolved, resolved.release_kind)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
