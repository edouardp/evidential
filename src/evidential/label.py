"""Fluent mark labels: ``label.fmt("num0").bold().auto_position("inside end")``.

All entry points return immutable :class:`~evidential.Label` specifications.
Pass a specification as ``label=`` on a mark, or to its ``.label(...)`` method.
"""

from ._label import Label as _Label

__all__ = [
    "fmt",
    "format",
    "font",
    "font_color",
    "color",
    "colour",
    "bold",
    "italic",
    "font_weight",
    "font_style",
    "figure_style",
    "source",
    "text",
    "value",
    "position",
    "auto_position",
    "align",
    "prefix",
    "suffix",
    "share",
    "overflow",
    "min_width",
]

_default = _Label()
fmt = _default.fmt
format = _default.format
font = _default.font
font_color = _default.font_color
color = _default.color
colour = _default.colour
bold = _default.bold
italic = _default.italic
font_weight = _default.font_weight
font_style = _default.font_style
figure_style = _default.figure_style
source = _default.source
text = _default.text
value = _default.value
position = _default.position
auto_position = _default.auto_position
align = _default.align
prefix = _default.prefix
suffix = _default.suffix
share = _default.share
overflow = _default.overflow
min_width = _default.min_width
