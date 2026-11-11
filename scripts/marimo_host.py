"""Print this machine's active Tailscale DNS name, or nothing for marimo defaults."""

from __future__ import annotations

import json
import re
import shutil
import subprocess


def tailscale_host() -> str | None:
    executable = shutil.which("tailscale")
    if executable is None:
        return None
    try:
        result = subprocess.run([executable, "status", "--json"], capture_output=True, text=True, check=True, timeout=2)
        status = json.loads(result.stdout)
    except (OSError, subprocess.SubprocessError, ValueError):
        return None
    if not isinstance(status, dict) or status.get("BackendState") != "Running":
        return None
    local = status.get("Self")
    if not isinstance(local, dict) or local.get("Online") is not True:
        return None
    name = local.get("DNSName")
    if not isinstance(name, str):
        return None
    host = name.removesuffix(".")
    if (
        not host
        or len(host) > 253
        or not all(re.fullmatch(r"(?!-)[A-Za-z0-9-]{1,63}(?<!-)", label) for label in host.split("."))
    ):
        return None
    return host


if __name__ == "__main__":
    if host := tailscale_host():
        print(host)
