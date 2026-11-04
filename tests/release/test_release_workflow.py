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
    for name in (
        "release.sh",
        "release_version.py",
        "release_state.py",
        "finish-release.sh",
        "publish.sh",
        "publish-guard.sh",
        "check-keyring.sh",
    ):
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
elif name == "uv" and args[:5] == ["run", "--frozen", "python", "-m", "keyring"] and args[5:6] == ["get"]:
    print("" if os.environ.get("RELEASE_TEST_EMPTY_TOKEN") else "fake-release-test-token")
elif name == "uv" and args[:1] == ["publish"]:
    assert os.environ.get("UV_PUBLISH_TOKEN") == "fake-release-test-token"
elif name == "gh" and args[:2] == ["release", "list"]:
    path = Path(".git/fake-github-release")
    if path.exists():
        print(path.read_text())
elif name == "gh" and args[:2] == ["release", "create"]:
    assert Path(args[args.index("--notes-file")+1]).read_text() == "Release notes.\\n"
    Path(".git/fake-github-release").write_text(args[2])
"""
    for name in ("make", "uv", "uvx", "gh", "editor"):
        executable = bin_dir / name
        executable.write_text(fake)
        executable.chmod(0o755)
    real_git = shutil.which("git")
    git_wrapper = bin_dir / "git"
    git_wrapper.write_text(
        "#!/usr/bin/env python3\nimport os, sys\n"
        'stage = os.environ.get("RELEASE_TEST_GIT_FAIL", "")\n'
        'if stage and " ".join(sys.argv[1:]).startswith(stage):\n'
        '    print("simulated git failure", file=sys.stderr)\n    sys.exit(19)\n'
        f"os.execv({real_git!r}, [{real_git!r}, *sys.argv[1:]])\n"
    )
    git_wrapper.chmod(0o755)
    # A dangling global wrapper reproduces the Homebrew interpreter failure.
    (bin_dir / "keyring").write_text("#!/missing/python3.14\n")
    (bin_dir / "keyring").chmod(0o755)
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
    assert [
        "uv",
        "run",
        "--frozen",
        "python",
        "-m",
        "keyring",
        "get",
        "https://upload.pypi.org/legacy/",
        "__token__",
    ] in calls
    assert sum("get" in call and "keyring" in call for call in calls) == 1
    assert calls.index(["make", "readme-check"]) < calls.index(["uv", "lock"])
    assert calls.index(["make", "validate"]) < calls.index(["make", "check"])
    upload = next(call for call in calls if call[:2] == ["uv", "publish"])
    assert set(upload[2:]) == {f"dist/evidential-{version}.tar.gz", f"dist/evidential-{version}-py3-none-any.whl"}
    github = next(call for call in calls if call[:3] == ["gh", "release", "create"])
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


def test_broken_managed_keyring_stops_before_version_edits_or_builds(release_repo):
    repository, _, _ = release_repo
    original = git(repository, "rev-parse", "HEAD")
    result, calls = run_release(release_repo, "minor", fail="uv run --frozen python -m keyring --help")
    assert result.returncode != 0 and "keyring CLI cannot start" in result.stderr
    assert calls == [["make", "readme-check"], ["uv", "run", "--frozen", "python", "-m", "keyring", "--help"]]
    assert git(repository, "rev-parse", "HEAD") == original
    assert git(repository, "status", "--porcelain") == ""


def test_direct_publish_checks_cli_startup_before_building_or_credentials(release_repo):
    repository, trace, env = release_repo
    result = subprocess.run(
        ["bash", "scripts/publish.sh"],
        cwd=repository,
        env={**env, "RELEASE_TEST_FAIL": "uv run --frozen python -m keyring --help"},
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode != 0 and "keyring CLI cannot start" in result.stderr
    assert [json.loads(line) for line in trace.read_text().splitlines()] == [
        ["uv", "run", "--frozen", "python", "-m", "keyring", "--help"]
    ]
    assert git(repository, "status", "--porcelain") == ""


@pytest.mark.parametrize(
    "stage", ["editor", "make validate", "make check", "uv run --frozen python -m keyring get", "uv publish"]
)
def test_failure_never_tags_or_creates_a_github_release(release_repo, stage):
    repository, _, _ = release_repo
    result, calls = run_release(release_repo, "patch", fail=stage)
    assert result.returncode != 0
    assert git(repository, "tag", "--list") == ""
    assert not any(call[0] == "gh" for call in calls)
    if stage not in {"uv run --frozen python -m keyring get", "uv publish"}:
        assert not any("get" in call and "keyring" in call for call in calls)
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
    assert not any(call[0] == "gh" or ("get" in call and "keyring" in call) for call in calls)
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


@pytest.mark.parametrize(
    "git_failure,github_failure",
    [
        ("push origin HEAD:", ""),
        ("tag v0.1.1", ""),
        ("push origin refs/tags/", ""),
        ("", "gh release list"),
        ("", "gh release create"),
    ],
)
def test_resume_after_upload_never_rebuilds_bumps_or_republishes(release_repo, git_failure, github_failure):
    repository, _, env = release_repo
    env["RELEASE_TEST_GIT_FAIL"] = git_failure
    result, calls = run_release(release_repo, "patch", fail=github_failure)
    assert result.returncode != 0 and "release-resume VERSION=0.1.1" in result.stderr
    receipt = json.loads((repository / ".git/evidential-release.json").read_text())
    assert receipt == {"version": "0.1.1", "commit": git(repository, "rev-parse", "HEAD"), "completed": False}
    published_calls = len(calls)
    commit = git(repository, "rev-parse", "HEAD")
    env.pop("RELEASE_TEST_GIT_FAIL")
    resumed, calls = run_release(release_repo, "--resume", "0.1.1")
    assert resumed.returncode == 0, resumed.stderr
    resumed_calls = calls[published_calls:]
    assert not any(call[0] in {"uv", "uvx", "make", "editor"} for call in resumed_calls)
    assert git(repository, "rev-parse", "HEAD") == commit
    assert git(repository, "rev-parse", "v0.1.1") == commit
    assert json.loads((repository / ".git/evidential-release.json").read_text())["completed"] is True
    assert sum(call[:2] == ["uv", "publish"] for call in calls) == 1
    # Repeating finalization is safe even if GitHub already created the release.
    before = len(calls)
    repeated, calls = run_release(release_repo, "--resume", "0.1.1")
    assert repeated.returncode == 0, repeated.stderr
    assert calls[before:][0][:3] == ["gh", "release", "list"]
    assert not any(call[:3] == ["gh", "release", "create"] for call in calls[before:])


def test_pending_upload_blocks_a_second_bump_and_resume_rejects_another_head(release_repo):
    repository, _, _ = release_repo
    result, calls = run_release(release_repo, "patch", fail="gh release create")
    assert result.returncode != 0
    before = len(calls)
    blocked, calls = run_release(release_repo, "patch")
    assert blocked.returncode != 0 and "release-resume" in blocked.stderr
    assert len(calls) == before
    git(repository, "commit", "--allow-empty", "-m", "Another commit")
    rejected, calls = run_release(release_repo, "--resume", "0.1.1")
    assert rejected.returncode != 0 and "does not match" in rejected.stderr
    assert len(calls) == before


def test_resume_refuses_missing_receipt_or_conflicting_tags(release_repo):
    repository, _, _ = release_repo
    result, calls = run_release(release_repo, "--resume", "0.1.0")
    assert result.returncode != 0 and "No successful-upload receipt" in result.stderr
    assert not calls
    run_release(release_repo, "patch", fail="gh release create")
    git(repository, "tag", "-d", "v0.1.1")
    git(repository, "tag", "v0.1.1", "HEAD~1")
    rejected, _ = run_release(release_repo, "--resume", "0.1.1")
    assert rejected.returncode != 0 and "points at another commit" in rejected.stderr


def test_finalization_uses_the_branch_upstream_remote(release_repo):
    repository, _, _ = release_repo
    git(repository, "remote", "rename", "origin", "publish")
    result, _ = run_release(release_repo, "patch")
    assert result.returncode == 0, result.stderr
    assert git(repository, "ls-remote", "publish", "refs/tags/v0.1.1").split()[0] == git(
        repository, "rev-parse", "HEAD"
    )


@pytest.mark.parametrize("matching", [False, True])
def test_remote_annotated_tag_is_checked_by_commit_and_never_overwritten(release_repo, matching):
    repository, _, env = release_repo
    env["RELEASE_TEST_GIT_FAIL"] = "push origin HEAD:"
    failed, _ = run_release(release_repo, "patch")
    assert failed.returncode != 0
    env.pop("RELEASE_TEST_GIT_FAIL")
    git(repository, "tag", "-a", "v0.1.1", "-m", "Existing remote tag", "HEAD" if matching else "HEAD~1")
    git(repository, "push", "origin", "refs/tags/v0.1.1")
    original = git(repository, "ls-remote", "origin", "refs/tags/v0.1.1")
    git(repository, "tag", "-d", "v0.1.1")
    resumed, _ = run_release(release_repo, "--resume", "0.1.1")
    assert (resumed.returncode == 0) is matching, resumed.stderr
    if not matching:
        assert "Remote tag" in resumed.stderr and "another commit" in resumed.stderr
    assert git(repository, "ls-remote", "origin", "refs/tags/v0.1.1") == original
