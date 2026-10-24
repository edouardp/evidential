"""Small, shared public-option alias handling; wire names remain stable."""

from typing import Any


def alias(options: dict[str, Any], canonical: str, compatibility: str) -> None:
    """Move an alias to its canonical key, rejecting conflicting declarations."""
    if compatibility not in options:
        return
    value = options.pop(compatibility)
    if value is None:
        return
    if options.get(canonical) is not None and options[canonical] != value:
        raise ValueError(f"{canonical} and {compatibility} disagree")
    options[canonical] = value


def format_code(format: str | None, fmt: str | None) -> str | None:
    """Resolve the public ``format`` spelling and its ``fmt`` compatibility alias."""
    options = {"fmt": fmt, "format": format}
    alias(options, "fmt", "format")
    return options.get("fmt")
