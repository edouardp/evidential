from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.release_version import ReleaseVersionError, parse_version, resolve_version

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "release_version.py"


@pytest.mark.parametrize(
    ("value", "is_prerelease"),
    [
        ("0.0.0", False),
        ("2.0.0", False),
        ("2.0.0a1", True),
        ("2.0.0b12", True),
        ("2.0.0rc3", True),
    ],
)
def test_parse_version_accepts_supported_canonical_versions(value: str, is_prerelease: bool) -> None:
    version = parse_version(value)

    assert str(version) == value
    assert version.is_prerelease is is_prerelease


@pytest.mark.parametrize(
    "value",
    [
        "2.0",
        "2.0.0-alpha.1",
        "2.0.0dev1",
        "2.0.0.post1",
        "2.0.0+local",
        "v2.0.0",
        "02.0.0",
        "2.0.0RC1",
        "2.0.0a",
    ],
)
def test_parse_version_rejects_unsupported_or_noncanonical_versions(value: str) -> None:
    with pytest.raises(ReleaseVersionError, match="expected X.Y.Z"):
        parse_version(value)


@pytest.mark.parametrize(
    ("current", "bump", "expected"),
    [
        ("1.2.3", "patch", "1.2.4"),
        ("1.2.3", "minor", "1.3.0"),
        ("1.2.3", "major", "2.0.0"),
    ],
)
def test_resolve_version_preserves_conventional_stable_bumps(
    current: str,
    bump: str,
    expected: str,
) -> None:
    assert str(resolve_version(current, bump)) == expected


@pytest.mark.parametrize(
    ("current", "requested"),
    [
        ("2.0.0", "2.0.0a1"),
        ("2.0.0a1", "2.0.0a2"),
        ("2.0.0a2", "2.0.0b1"),
        ("2.0.0b1", "2.0.0rc1"),
        ("2.0.0rc1", "2.0.0"),
    ],
)
def test_resolve_version_accepts_explicit_release_cycle_transitions(
    current: str,
    requested: str,
) -> None:
    assert str(resolve_version(current, requested)) == requested


def test_explicit_bootstrap_can_move_unpublished_stable_source_to_alpha() -> None:
    resolved = resolve_version("2.0.0", "2.0.0a1")

    assert resolved.release_kind == "prerelease"


def test_automatic_bump_from_prerelease_requires_explicit_version() -> None:
    with pytest.raises(ReleaseVersionError, match="use --version"):
        resolve_version("2.0.0a1", "patch")


def test_requesting_current_version_is_rejected() -> None:
    with pytest.raises(ReleaseVersionError, match="already current"):
        resolve_version("2.0.0a1", "2.0.0a1")


def test_cli_classifies_prerelease_for_release_script() -> None:
    result = subprocess.run(
        [sys.executable, SCRIPT, "2.0.0", "--version", "2.0.0a1"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout == "2.0.0a1 prerelease\n"


def test_make_release_with_version_bypasses_interactive_chooser() -> None:
    result = subprocess.run(
        ["make", "--no-print-directory", "--dry-run", "release", "VERSION=2.0.0a1"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip() == './scripts/release.sh --version "2.0.0a1"'
    assert "chooser.py" not in result.stdout
