"""Host discovery fails closed; the real Make recipe preserves explicit overrides."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

from scripts.marimo_host import tailscale_host

ROOT = Path(__file__).resolve().parents[2]
ACTIVE = {"BackendState": "Running", "Self": {"Online": True, "DNSName": "my-mini.example.ts.net."}}


def test_missing_cli_does_not_start_a_process(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda _name: None)
    run = Mock()
    monkeypatch.setattr(subprocess, "run", run)
    assert tailscale_host() is None
    run.assert_not_called()


@pytest.mark.parametrize(
    "status",
    [
        [],
        {},
        {"BackendState": "Stopped"},
        {**ACTIVE, "Self": None},
        {**ACTIVE, "Self": {**ACTIVE["Self"], "Online": False}},
        *[
            {**ACTIVE, "Self": {**ACTIVE["Self"], "DNSName": value}}
            for value in [None, "", "bad host.ts.net.", "--host", "a..ts.net.", "a/evil.ts.net.", "-bad.ts.net."]
        ],
    ],
)
def test_inactive_or_unusable_status_omits_host(monkeypatch, status):
    monkeypatch.setattr(shutil, "which", lambda _name: "/fake/tailscale")
    monkeypatch.setattr(subprocess, "run", lambda *_args, **_kwargs: Mock(stdout=json.dumps(status)))
    assert tailscale_host() is None


@pytest.mark.parametrize(
    "error",
    [OSError("missing"), subprocess.TimeoutExpired("tailscale", 2), subprocess.CalledProcessError(1, "tailscale")],
)
def test_cli_failure_or_timeout_is_silent_fallback(monkeypatch, error):
    monkeypatch.setattr(shutil, "which", lambda _name: "/fake/tailscale")
    monkeypatch.setattr(subprocess, "run", Mock(side_effect=error))
    assert tailscale_host() is None


def test_invalid_json_is_silent_fallback(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda _name: "/fake/tailscale")
    monkeypatch.setattr(subprocess, "run", lambda *_args, **_kwargs: Mock(stdout="not JSON"))
    assert tailscale_host() is None


@pytest.mark.parametrize("cli", ["active", "missing", "stopped", "failed", "invalid"])
@pytest.mark.parametrize(
    "source,override",
    [(None, None), ("command", "127.0.0.1"), ("command", ""), ("environment", "127.0.0.1"), ("environment", "")],
)
def test_run_marimo_passes_only_the_selected_host(tmp_path, cli, source, override):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "python3").symlink_to(sys.executable)
    (bin_dir / "date").symlink_to(shutil.which("date"))
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copy2(ROOT / "scripts/marimo_host.py", scripts)
    marker = tmp_path / "queried"
    if cli != "missing":
        executable = bin_dir / "tailscale"
        executable.write_text(
            f"#!{sys.executable}\nimport os, sys\nfrom pathlib import Path\n"
            f"Path({str(marker)!r}).touch()\n"
            'print(os.environ["TAILSCALE_TEST_STATUS"])\n'
            f"sys.exit({1 if cli == 'failed' else 0})\n"
        )
        executable.chmod(0o755)
    uv = bin_dir / "uv"
    uv.write_text(f"#!{sys.executable}\nimport json,sys\nprint(json.dumps(sys.argv[1:]))\n")
    uv.chmod(0o755)
    status = ACTIVE if cli == "active" else {"BackendState": "Stopped"}
    environment = {
        key: value for key, value in os.environ.items() if key not in {"HOST", "MAKEFLAGS", "MFLAGS", "MAKEOVERRIDES"}
    }
    if source == "environment":
        environment["HOST"] = override
    result = subprocess.run(
        [
            shutil.which("make"),
            "-f",
            str(ROOT / "Makefile"),
            "run-marimo",
            *([f"HOST={override}"] if source == "command" else []),
        ],
        cwd=tmp_path,
        env={
            **environment,
            "PATH": str(bin_dir),
            "TAILSCALE_TEST_STATUS": "invalid" if cli == "invalid" else json.dumps(status),
        },
        capture_output=True,
        text=True,
        check=True,
    )
    arguments = json.loads(result.stdout)
    selected = "my-mini.example.ts.net" if override is None and cli == "active" else override
    assert arguments == [
        "run",
        "marimo",
        "edit",
        "--watch",
        "--no-sandbox",
        *(["--host", selected] if selected else []),
        "notebooks",
    ]
    assert not result.stderr
    assert marker.exists() is (cli != "missing" and override is None)
