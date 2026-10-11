"""ADRs stay numbered, front-mattered, linked and indexed."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ADR_DIR = ROOT / "docs" / "adr"
INDEX = ADR_DIR / "README.md"
ADR_FILES = sorted(path for path in ADR_DIR.glob("*.md") if path.name != "README.md")
IDENTIFIER = re.compile(r"^(\d{3})-([a-z0-9-]+)\.md$")
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _frontmatter(path: Path) -> dict[str, str]:
    match = FRONTMATTER.match(path.read_text())
    assert match, f"{path.name} is missing YAML frontmatter"
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def test_there_are_adrs() -> None:
    assert ADR_FILES, "docs/adr must contain at least one decision record"


@pytest.mark.parametrize("path", ADR_FILES, ids=lambda path: path.name)
def test_adr_filenames_are_numbered_and_slugged(path: Path) -> None:
    assert IDENTIFIER.match(path.name), f"{path.name} must be NNN-kebab-case.md"


@pytest.mark.parametrize("path", ADR_FILES, ids=lambda path: path.name)
def test_adr_frontmatter_is_complete(path: Path) -> None:
    fields = _frontmatter(path)
    assert fields.get("status"), "status is required"
    assert fields.get("date"), "date is required"
    assert fields.get("deciders"), "deciders is required"
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", fields["date"]), fields["date"]


def test_adr_numbers_are_unique() -> None:
    numbers = [IDENTIFIER.match(path.name).group(1) for path in ADR_FILES]
    assert len(numbers) == len(set(numbers)), "duplicate ADR numbers"


def test_adr_index_lists_every_record_in_order() -> None:
    index = INDEX.read_text()
    listed = re.findall(r"\[\d{3}\]\((\d{3}-[a-z0-9-]+\.md)\)", index)
    expected = [path.name for path in ADR_FILES]
    assert listed == expected, "ADR index is out of date"


def test_adr_links_in_readme_resolve() -> None:
    readme = (ROOT / "README.md").read_text()
    for target in re.findall(r"\((docs/adr/[^)]+)\)", readme):
        assert (ROOT / target).exists(), target
