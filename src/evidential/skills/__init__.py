"""Locate the agent skill bundled with this installation of Evidential."""

from pathlib import Path

__all__ = ["path"]


def path() -> Path:
    """Return the directory containing the version-matched SKILL.md and resources.

    The returned path belongs to the installed package (or editable checkout).
    Reading it does not install a skill into an agent's configuration.
    """
    return Path(__file__).resolve().parent / "developing-with-evidential"
