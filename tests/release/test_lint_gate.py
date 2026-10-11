"""Every lint stage must block the run when its tool fails.

This drives the real ``scripts/lint.sh`` orchestration with fake tools on the
``PATH`` so the shell logic (fail-fast, diagnostics preserved) is exercised
without touching the checkout.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
STAGES = (
    "uv run ruff check",
    "uv run ruff format",
    "uv run bandit",
    "uv run pip-audit",
    "uv run pyrefly",
    "shellcheck",
    "checkmake",
    "uvx rumdl",
)


def run_lint(tmp_path: Path, *, fail_stage: str = "", fix: bool = False) -> subprocess.CompletedProcess[str]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for command in ("uv", "uvx", "shellcheck", "checkmake"):
        executable = bin_dir / command
        executable.write_text(
            "#!/usr/bin/env bash\n"
            'invocation="${0##*/} $*"\n'
            'echo "$invocation"\n'
            'if [[ -n "$FAIL_STAGE" && "$invocation" == "$FAIL_STAGE"* ]]; then\n'
            '    echo "diagnostic: $FAIL_STAGE failed" >&2\n'
            "    exit 23\n"
            "fi\n"
        )
        executable.chmod(0o755)
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "example.sh").touch()
    return subprocess.run(
        ["bash", str(ROOT / "scripts/lint.sh"), *(["--fix"] if fix else [])],
        cwd=tmp_path,
        env={
            **os.environ,
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            "FAIL_STAGE": fail_stage,
        },
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("fix", [False, True])
@pytest.mark.parametrize("fail_stage", STAGES)
def test_lint_failure_is_fatal_and_preserves_diagnostics(tmp_path: Path, fail_stage: str, fix: bool) -> None:
    result = run_lint(tmp_path, fail_stage=fail_stage, fix=fix)

    assert result.returncode != 0
    assert f"diagnostic: {fail_stage} failed" in result.stderr
    assert "All lints passed" not in result.stdout
    for later_stage in STAGES[STAGES.index(fail_stage) + 1 :]:
        assert later_stage not in result.stdout


@pytest.mark.parametrize("fix", [False, True])
def test_lint_success_runs_all_stages(tmp_path: Path, fix: bool) -> None:
    result = run_lint(tmp_path, fix=fix)

    assert result.returncode == 0, result.stderr
    for stage in STAGES:
        assert stage in result.stdout
    assert "All lints passed" in result.stdout
