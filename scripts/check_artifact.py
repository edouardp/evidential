"""Verify the built distributions are complete and clean.

Run by ``make check-artifact`` after ``make build``. The checks assert that the
shipped wheel/sdist contain every runtime module plus the committed renderer
assets, and that no development files (tests, notebooks, the JS sources) leak
into a release.
"""

from __future__ import annotations

import sys
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

PACKAGE = "evidential"
REQUIRED = (
    f"{PACKAGE}/__init__.py",
    f"{PACKAGE}/_compat.py",
    f"{PACKAGE}/_column_options.py",
    f"{PACKAGE}/aggregations.py",
    f"{PACKAGE}/client.py",
    f"{PACKAGE}/comparison.py",
    f"{PACKAGE}/configuration.py",
    f"{PACKAGE}/data.py",
    f"{PACKAGE}/duck.py",
    f"{PACKAGE}/grouped.py",
    f"{PACKAGE}/live.py",
    f"{PACKAGE}/pivot.py",
    f"{PACKAGE}/query.py",
    f"{PACKAGE}/rules.py",
    f"{PACKAGE}/table.py",
    f"{PACKAGE}/py.typed",
    f"{PACKAGE}/static/table.js",
    f"{PACKAGE}/static/table.css",
)
FORBIDDEN = ("tests/", "notebooks/", "frontend/", "__pycache__", ".pyc", ".coverage")
MIN_RENDERER_BYTES = 10_000
RENDERER_ASSETS = (f"{PACKAGE}/static/table.js", f"{PACKAGE}/static/table.css")


def _normalize(name: str) -> str:
    """Map an archive member to its package-relative name."""
    marker = f"{PACKAGE}/"
    index = name.find(marker)
    return name[index:] if index != -1 else name


def wheel_members(path: Path) -> dict[str, bytes]:
    """Return ``{package-relative name: bytes}`` for a wheel."""
    with zipfile.ZipFile(path) as archive:
        return {_normalize(name): archive.read(name) for name in archive.namelist() if not name.endswith("/")}


def sdist_members(path: Path) -> dict[str, bytes]:
    """Return ``{package-relative name: bytes}`` for a source distribution."""
    members: dict[str, bytes] = {}
    with tarfile.open(path) as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            handle = archive.extractfile(member)
            if handle is not None:
                members[_normalize(member.name)] = handle.read()
    return members


def inspect(members: dict[str, bytes]) -> list[str]:
    """Return a list of problems with an archive's members (empty means good)."""
    problems = [f"missing {name}" for name in REQUIRED if name not in members]
    problems += [f"unexpected dev file: {name}" for name in members if any(part in name for part in FORBIDDEN)]
    for name in RENDERER_ASSETS:
        if name in members and len(members[name]) < MIN_RENDERER_BYTES:
            problems.append(f"{name} looks empty ({len(members[name])} bytes)")
    return problems


def discover() -> tuple[list[Path], list[Path]]:
    """Find the wheels and sdists in ``dist/``."""
    wheels = sorted(DIST.glob("*.whl"))
    sdists = sorted(DIST.glob("*.tar.gz"))
    return wheels, sdists


def main() -> int:
    wheels, sdists = discover()
    if not wheels or not sdists:
        print("error: run `make build` first (no wheel/sdist found in dist/)", file=sys.stderr)
        return 1
    failed = False
    for path, reader in (
        *((path, wheel_members) for path in wheels),
        *((path, sdist_members) for path in sdists),
    ):
        problems = inspect(reader(path))
        if problems:
            failed = True
            print(f"FAIL {path.name}")
            for problem in problems:
                print(f"  - {problem}")
        else:
            print(f"ok   {path.name}")
    if failed:
        return 1
    print(f"Checked {len(wheels)} wheel(s) and {len(sdists)} sdist(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
