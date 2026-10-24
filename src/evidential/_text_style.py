"""Shared fluent formatting and typography for columns and mark labels."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Self


class TextStyle(ABC):
    """Typography refinements; subclasses provide immutable copying and wire keys."""

    __slots__ = ()
    _format_key: ClassVar[str] = "fmt"
    _text_color_key: ClassVar[str] = "font_color"

    @abstractmethod
    def _with(self, **changes: Any) -> Self:
        """Return an independent specification with the supplied refinements."""

    def fmt(self, code: str) -> Self:
        """Set the value format code.

        ``code`` is a named preset (``"usd0"``, ``"pct1"``, ``"num0k"``, ``"yyyy"``,
        ``"flag"``…) or a raw Excel/``ssf`` pattern. This is the escape hatch for
        anything the column kinds do not cover.

        Example::

            col.number("sales").fmt("usd0")
        """
        return self._with(**{self._format_key: code})

    def figure_style(self, value: str) -> Self:
        """Override the CSS ``font-variant-numeric`` for this text.

        The default is ``"lining-nums tabular-nums"``; pass e.g.
        ``"oldstyle-nums proportional-nums"``.

        Example::

            col.text("amount").figure_style("lining-nums proportional-nums")
        """
        return self._with(figure_style=value)

    def font(self, family: str) -> Self:
        """Set the CSS ``font-family`` for this text.

        Example::

            col.text("code").font("ui-monospace, monospace")
        """
        return self._with(font=family)

    def font_color(self, color: str) -> Self:
        """Set the text colour (any CSS colour).

        Example::

            col.number("change").font_color("#b91c1c")
        """
        return self._with(**{self._text_color_key: color})

    def bold(self, value: bool = True) -> Self:
        """Render this text in bold.

        Example::

            col.text("item").bold()
        """
        return self._with(font_weight="600" if value else None)

    def italic(self, value: bool = True) -> Self:
        """Render this text in italics.

        Example::

            col.text("note").italic()
        """
        return self._with(font_style="italic" if value else None)

    def font_weight(self, value: str) -> Self:
        """Set the CSS ``font-weight`` (e.g. ``"600"``, ``"bold"``).

        Example::

            col.text("total").font_weight("700")
        """
        return self._with(font_weight=value)

    def font_style(self, value: str) -> Self:
        """Set the CSS ``font-style`` (e.g. ``"italic"``, ``"oblique"``).

        Example::

            col.text("note").font_style("oblique")
        """
        return self._with(font_style=value)

    format = fmt
