"""Theme-aware colours usable anywhere a colour string is accepted."""

from __future__ import annotations

import math
from typing import Literal


def fixed(value: str) -> str:
    """Keep an exact CSS/matplotlib colour even with ``adapt_colors=True``."""
    if not isinstance(value, str) or not value.strip() or value.startswith(("fixed:", "theme:")):
        raise ValueError("fixed() needs a literal CSS or matplotlib colour")
    return f"fixed:{value}"


def theme(
    role: Literal["surface", "neutral", "text", "muted", "accent", "positive", "negative"],
    *,
    alpha: float = 1,
) -> str:
    """Resolve a semantic colour in the widget's scheme, preserving opacity.

    ``neutral`` is the surface colour; use it for a diverging palette's centre.
    For example: ``["red", color.theme("neutral", alpha=0.8), "blue"]``.
    """
    if role not in ("surface", "neutral", "text", "muted", "accent", "positive", "negative"):
        raise ValueError(f"Unknown theme colour: {role!r}")
    if (
        isinstance(alpha, bool)
        or not isinstance(alpha, (int, float))
        or not math.isfinite(alpha)
        or not 0 <= alpha <= 1
    ):
        raise ValueError("alpha must be a finite number between 0 and 1")
    return f"theme:{role}/{alpha:g}"
