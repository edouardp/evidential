"""Print this machine's active Tailscale DNS name, or nothing for marimo defaults."""

from __future__ import annotations

import json
import subprocess


def tailscale_host() -> str | None:
    try:
        status = json.loads(
            subprocess.check_output(["tailscale", "status", "--json"], text=True, stderr=subprocess.DEVNULL, timeout=2)
        )
        if status["BackendState"] == "Running" and status["Self"]["Online"]:
            name = status["Self"]["DNSName"]
            if isinstance(name, str):
                return name.removesuffix(".") or None
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError):
        return None
    return None


if __name__ == "__main__":
    if host := tailscale_host():
        print(host)
