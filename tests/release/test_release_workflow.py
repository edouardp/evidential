"""Exercise the real release scripts in local repos with fake publishing tools."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def git(repository, *args):
    return subprocess.run(["git", *args], cwd=repository, check=True, text=True, capture_output=True).stdout.strip()


@pytest.fixture
def release_repo(tmp_path):
    repository = tmp_path / "repo"
    scripts = repository / "scripts"
    scripts.mkdir(parents=True)
    for name in ("release.sh", "release_version.py", "publish.sh", "publish-guard.sh"):
        shutil.copy2(ROOT / "scripts" / name, scripts / name)
    (repository / "pyproject.toml").write_text('[project]\nname = "evidential"\nversion = "0.1.0"\n')
    (repository / "uv.lock").write_text('version = "0.1.0"\n')
    (repository / "CHANGELOG.md").write_text("# Changelog\n\n## 0.1.0 (2026-10-26)\n\nFirst release.\n")
    (repository / ".gitignore").write_text("dist/\n")
    git(repository, "init", "--initial-branch=release-demo")
    git(repository, "config", "user.name", "Release Test")
    git(repository, "config", "user.email", "release@example.invalid")
    git(repository, "add", ".")
    git(repository, "commit", "-m", "Initial")
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "--bare", str(remote))
    git(repository, "remote", "add", "origin", str(remote))
    git(repository, "push", "--set-upstream", "origin", "release-demo")

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    # These executables replace every external publishing/editor/build command.
    # No real keyring, upload service or GitHub command is ever invoked.
    fake = """#!/usr/bin/env python3
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib

name = Path(sys.argv[0]).name
args = sys.argv[1:]
with open(os.environ["RELEASE_TEST_TRACE"], "a") as trace:
    trace.write(json.dumps([name, *args]) + "\\n")
invocation = " ".join([name, *args])
if os.environ.get("RELEASE_TEST_FAIL") and invocation.startswith(os.environ["RELEASE_TEST_FAIL"]):
    print("simulated failure: " + invocation, file=sys.stderr)
    sys.exit(17)
if name == "editor" and not os.environ.get("RELEASE_TEST_SKIP_EDITOR"):
    path = Path(args[0])
    path.write_text(path.read_text().replace("<!-- Fill in release notes, then save and close -->", "Release notes."))
elif name == "uv" and args == ["lock"]:
    version = tomllib.loads(Path("pyproject.toml").read_text())["project"]["version"]
    Path("uv.lock").write_text(f'version = "{version}"\\n')
elif name == "make" and args == ["pypi"]:
    sys.exit(subprocess.run(["bash", "scripts/publish.sh"]).returncode)
elif name == "make" and args == ["check"]:
    version = tomllib.loads(Path("pyproject.toml").read_text())["project"]["version"]
    Path("dist").mkdir(exist_ok=True)
    Path(f"dist/evidential-{version}.tar.gz").touch()
    Path(f"dist/evidential-{version}-py3-none-any.whl").touch()
elif name == "keyring":
    print("" if os.environ.get("RELEASE_TEST_EMPTY_TOKEN") else "fake-release-test-token")
elif name == "uv" and args[:1] == ["publish"]:
    assert os.environ.get("UV_PUBLISH_TOKEN") == "fake-release-test-token"
"""
    for name in ("make", "uv", "uvx", "keyring", "gh", "editor"):
        executable = bin_dir / name
        executable.write_text(fake)
        executable.chmod(0o755)
    trace = tmp_path / "trace.jsonl"
    env = {
        **os.environ,
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "EDITOR": "editor",
        "RELEASE_TEST_TRACE": str(trace),
    }
    return repository, trace, env


def run_release(fixture, *args, fail=""):
    repository, trace, env = fixture
    result = subprocess.run(
        ["bash", "scripts/release.sh", *args],
        cwd=repository,
        env={**env, "RELEASE_TEST_FAIL": fail},
        check=False,
        text=True,
        capture_output=True,
    )
    calls = [json.loads(line) for line in trace.read_text().splitlines()] if trace.exists() else []
    return result, calls


@pytest.mark.parametrize(
    "version_request,version,prerelease", [("minor", "0.2.0", False), ("0.2.0rc1", "0.2.0rc1", True)]
)
def test_release_bumps_changelog_validates_publishes_tags_and_creates_github_release(
    release_repo, version_request, version, prerelease
):
    repository, _, _ = release_repo
    args = ["--version", version_request] if prerelease else [version_request]
    result, calls = run_release(release_repo, *args)
    assert result.returncode == 0, result.stderr
    assert f'version = "{version}"' in (repository / "pyproject.toml").read_text()
    assert f"## {version} (" in (repository / "CHANGELOG.md").read_text()
    assert "Release notes." in (repository / "CHANGELOG.md").read_text()
    assert ["keyring", "get", "https://upload.pypi.org/legacy/", "__token__"] in calls
    assert sum(call[0] == "keyring" for call in calls) == 1
    assert calls.index(["make", "readme-check"]) < calls.index(["uv", "lock"])
    assert calls.index(["make", "validate"]) < calls.index(["make", "check"])
    upload = next(call for call in calls if call[:2] == ["uv", "publish"])
    assert set(upload[2:]) == {f"dist/evidential-{version}.tar.gz", f"dist/evidential-{version}-py3-none-any.whl"}
    github = next(call for call in calls if call[0] == "gh")
    assert github[:4] == ["gh", "release", "create", f"v{version}"]
    assert ("--prerelease" in github) is prerelease
    assert git(repository, "log", "-1", "--pretty=%s") == f"Release v{version}"
    assert git(repository, "rev-parse", f"v{version}") == git(repository, "rev-parse", "HEAD")
    assert git(repository, "status", "--porcelain") == ""
    assert "fake-release-test-token" not in result.stdout + result.stderr


def test_stale_readme_stops_before_any_version_change_editor_or_commit(release_repo):
    repository, _, _ = release_repo
    original = git(repository, "rev-parse", "HEAD")
    result, calls = run_release(release_repo, "minor", fail="make readme-check")
    assert result.returncode != 0
    assert calls == [["make", "readme-check"]]
    assert git(repository, "rev-parse", "HEAD") == original
    assert git(repository, "status", "--porcelain") == ""


@pytest.mark.parametrize("stage", ["editor", "make validate", "make check", "keyring get", "uv publish"])
def test_failure_never_tags_or_creates_a_github_release(release_repo, stage):
    repository, _, _ = release_repo
    result, calls = run_release(release_repo, "patch", fail=stage)
    assert result.returncode != 0
    assert git(repository, "tag", "--list") == ""
    assert not any(call[0] == "gh" for call in calls)
    if stage not in {"keyring get", "uv publish"}:
        assert not any(call[0] == "keyring" for call in calls)
    if stage != "uv publish":
        assert not any(call[:2] == ["uv", "publish"] for call in calls)


def test_invalid_version_stops_before_any_mutation(release_repo):
    repository, _, _ = release_repo
    result, calls = run_release(release_repo, "--version", "invalid")
    assert result.returncode != 0
    assert calls == []
    assert git(repository, "status", "--porcelain") == ""


def test_existing_tag_stops_before_version_change(release_repo):
    repository, _, _ = release_repo
    git(repository, "tag", "v0.2.0")
    result, calls = run_release(release_repo, "minor")
    assert result.returncode != 0 and "already exists" in result.stderr
    assert calls == []
    assert git(repository, "status", "--porcelain") == ""


def test_untouched_changelog_stops_before_commit_or_credentials(release_repo):
    repository, _, env = release_repo
    env["RELEASE_TEST_SKIP_EDITOR"] = "1"
    before = git(repository, "rev-parse", "HEAD")
    result, calls = run_release(release_repo, "minor")
    assert result.returncode != 0 and "Changelog not edited" in result.stderr
    assert git(repository, "rev-parse", "HEAD") == before
    assert not any(call[0] in {"keyring", "gh"} for call in calls)
    assert 'version = "0.2.0"' in (repository / "pyproject.toml").read_text()


def test_empty_token_is_never_sent_to_pypi(release_repo):
    repository, _, env = release_repo
    env["RELEASE_TEST_EMPTY_TOKEN"] = "1"
    result, calls = run_release(release_repo, "minor")
    assert result.returncode != 0 and "token is empty" in result.stderr
    assert not any(call[:2] == ["uv", "publish"] for call in calls)
    assert not any(call[0] == "gh" for call in calls)
    assert git(repository, "tag", "--list") == ""


def test_build_prunes_previous_distributions_before_building():
    result = subprocess.run(["make", "--dry-run", "build"], cwd=ROOT, check=True, text=True, capture_output=True)
    assert result.stdout.index("rm -rf dist/") < result.stdout.index("uv build")
