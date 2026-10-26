from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLISH_GUARD = ROOT / "scripts" / "publish-guard.sh"


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def _repository(tmp_path: Path, *, upstream: bool = True) -> Path:
    repository = tmp_path / "repository"
    scripts = repository / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy2(PUBLISH_GUARD, scripts / PUBLISH_GUARD.name)

    _git("init", "--initial-branch=galaga_v2", cwd=repository)
    _git("config", "user.name", "Release Guard Test", cwd=repository)
    _git("config", "user.email", "release-guard@example.invalid", cwd=repository)
    _git("add", ".", cwd=repository)
    _git("commit", "-m", "Initialize test repository", cwd=repository)

    if upstream:
        remote = tmp_path / "remote.git"
        _git("init", "--bare", str(remote), cwd=tmp_path)
        _git("remote", "add", "origin", str(remote), cwd=repository)
        _git("push", "--set-upstream", "origin", "galaga_v2", cwd=repository)

    return repository


def _run_guard(repository: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", repository / "scripts" / PUBLISH_GUARD.name],
        cwd=repository,
        check=False,
        capture_output=True,
        text=True,
    )


def test_clean_non_main_release_branch_with_upstream_is_allowed(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    result = _run_guard(repository)

    assert result.returncode == 0
    assert "Release branch: galaga_v2 -> origin/galaga_v2" in result.stdout


def test_dirty_release_branch_is_rejected(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    (repository / "dirty.txt").write_text("not committed\n")

    result = _run_guard(repository)

    assert result.returncode == 1
    assert "Working tree is dirty" in result.stderr


def test_release_branch_without_upstream_is_rejected(tmp_path: Path) -> None:
    repository = _repository(tmp_path, upstream=False)

    result = _run_guard(repository)

    assert result.returncode == 1
    assert "has no configured upstream" in result.stderr


def test_detached_head_is_rejected(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    _git("checkout", "--detach", cwd=repository)

    result = _run_guard(repository)

    assert result.returncode == 1
    assert "detached HEAD is not supported" in result.stderr
