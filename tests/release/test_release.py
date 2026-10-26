"""Release-workflow guardrails: metadata, changelog and local validation."""

from __future__ import annotations

import os
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text())
PROJECT = PYPROJECT["project"]


def test_pyproject_declares_release_metadata() -> None:
    assert PROJECT["name"] == "evidential"
    assert PROJECT["license"] == "MIT"
    assert PROJECT["license-files"] == ["LICENSE"]
    assert PROJECT["readme"] == "docs/PYPI_README.md"
    assert (ROOT / "LICENSE").exists()

    classifiers = PROJECT["classifiers"]
    assert "Programming Language :: Python :: 3.11" in classifiers
    assert any(classifier.startswith("Topic ::") for classifier in classifiers)
    # PEP 639: the license comes from `project.license` + `license-files`, not a
    # deprecated License classifier.
    assert not any(classifier.startswith("License ::") for classifier in classifiers)

    urls = PROJECT["urls"]
    assert {"Homepage", "Repository", "Issues", "Changelog"} <= set(urls)
    assert all(url.startswith("https://") for url in urls.values())


def test_changelog_has_an_entry_for_the_current_version() -> None:
    version = PROJECT["version"]
    changelog = (ROOT / "CHANGELOG.md").read_text()
    assert changelog.startswith("# Changelog")
    assert re.search(rf"^## {re.escape(version)} \(", changelog, re.MULTILINE), version


def test_release_script_bumps_checks_and_publishes() -> None:
    script = ROOT / "scripts" / "release.sh"
    assert script.exists()
    assert os.access(script, os.X_OK)
    text = script.read_text()
    for token in (
        "pyproject.toml",
        "CHANGELOG.md",
        "make readme-check",
        "make validate",
        "make pypi",
        "release create",
    ):
        assert token in text, token
    assert (ROOT / "scripts" / "chooser.py").exists()


def test_makefile_exposes_the_release_targets() -> None:
    makefile = (ROOT / "Makefile").read_text()
    for target in ("release:", "release-patch:", "release-minor:", "release-major:", "check:", "pypi:"):
        assert re.search(rf"^{re.escape(target)}", makefile, re.MULTILINE), target


def test_direct_publish_and_release_share_the_house_keyring_flow() -> None:
    makefile = (ROOT / "Makefile").read_text()
    publish = (ROOT / "scripts/publish.sh").read_text()
    assert "./scripts/publish.sh" in makefile
    assert "make pypi" in (ROOT / "scripts/release.sh").read_text()
    assert (
        "UV_PUBLISH_TOKEN=$(uv run --frozen python -m keyring get https://upload.pypi.org/legacy/ __token__)" in publish
    )
    assert "export UV_PUBLISH_TOKEN" in publish
    assert "uv publish dist/*" in publish
    assert publish.index("make readme-check") < publish.index("-m keyring get")
    assert publish.index("make check") < publish.index("-m keyring get")


def test_releases_use_complete_local_gates_without_github_actions() -> None:
    workflows = ROOT / ".github" / "workflows"
    assert not [*workflows.glob("*.yml"), *workflows.glob("*.yaml")]
    makefile = (ROOT / "Makefile").read_text()
    validation = next(line for line in makefile.splitlines() if line.startswith("validate:")).split("##", 1)[0]
    for gate in ("lint", "check-notebooks", "readme-check", "test", "frontend-check", "test-browser", "build"):
        assert gate in validation.split(), f"make validate must run {gate} locally"
    assert "EVIDENTIAL_REQUIRE_BROWSER=1 uv run pytest -m browser" in makefile
    release_doc = (ROOT / "docs" / "RELEASE_PROCESS.md").read_text()
    assert "Buildkite" in release_doc
    assert "make check" in release_doc
