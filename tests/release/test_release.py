"""Release-workflow guardrails: metadata, changelog, release script and CI."""

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
    for token in ("pyproject.toml", "CHANGELOG.md", "make validate", "make build", "twine check", "uv publish"):
        assert token in text, token
    assert (ROOT / "scripts" / "chooser.py").exists()


def test_makefile_exposes_the_release_targets() -> None:
    makefile = (ROOT / "Makefile").read_text()
    for target in ("release:", "release-patch:", "release-minor:", "release-major:", "check:", "pypi:"):
        assert re.search(rf"^{re.escape(target)}", makefile, re.MULTILINE), target


def test_direct_publish_uses_the_same_keyring_provider_as_the_release_script() -> None:
    makefile = (ROOT / "Makefile").read_text()
    publish = makefile.split("pypi: check", 1)[1].split("\n\n", 1)[0]
    assert "uv publish --keyring-provider subprocess --username __token__" in publish


def test_ci_workflow_runs_the_gates() -> None:
    workflow = (ROOT / ".github" / "workflows" / "tests.yml").read_text()
    assert "make lint" in workflow
    assert "make check-notebooks" in workflow
    assert "make test-python" in workflow
    assert "make frontend-test" in workflow
    assert "make check-artifact" in workflow
    assert "make frontend-check" in workflow
    assert "make test-browser" in workflow
    assert 'EVIDENTIAL_REQUIRE_BROWSER: "1"' in workflow
    assert "playwright install --with-deps chromium" in workflow
    classifiers = PROJECT["classifiers"]
    supported = [value.rsplit(" ", 1)[-1] for value in classifiers if re.search(r" :: 3\.\d+$", value)]
    for version in supported:
        assert f'"{version}"' in workflow
    assert "uv sync --locked" in workflow
    assert "pip install --upgrade uv" not in workflow
    assert "checkmake@latest" not in workflow
