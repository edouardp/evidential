"""Typed public configuration and runtime validation of canonical options."""

from __future__ import annotations

import math
import types
from collections.abc import Callable, Mapping, Sequence
from difflib import get_close_matches
from functools import cache
from typing import Any, Literal, TypedDict, Union, Unpack, cast, get_args, get_origin, get_type_hints, is_typeddict

Length = str | float
Palette = str | Sequence[str]
Rotation = Literal["vertical"] | float
FigureStyle = Literal[
    "oldstyle",
    "oldstyle-tabular",
    "proportional",
    "lining-proportional",
    "oldstyle-proportional",
    "lining",
    "tabular",
    "lining-tabular",
    "default",
    "auto",
    "none",
]
#: Relative-time rendering for a date/time column: ``True`` (auto unit) or a unit.
Relative = bool | Literal["second", "minute", "hour", "day", "week", "month", "year"]


class DefaultSort(TypedDict, total=False):
    column: str
    direction: Literal["asc", "desc"]


class Theme(TypedDict, total=False):
    background: str | None
    surface: str | None
    dialog_background: str | None
    text: str | None
    muted: str | None
    border: str | None
    row_border: str | None
    header_bg: str | None
    header_border: str | None
    header_text: str | None
    hover: str | None
    shading: str | None
    total_bg: str | None
    total_text: str | None
    subtotal_bg: str | None
    pivot_bg: str | None
    link: str | None
    negative: str | None
    accent: str | None
    font: str | None
    font_size: str | None


class TableOptions(TypedDict, total=False):
    title: str | None
    subtitle: str | None
    caption: str | None
    null_text: str | None
    stub: str | None
    stub_head: str | None
    footnote_marks: Literal["numbers", "letters", "symbols"] | None
    all_caps: bool
    stretch: bool
    align_decimals: bool
    group_gap: bool
    rotate_titles: Rotation | None
    figure_style: FigureStyle | None
    font_size: float | str | None
    footnote_column: str | None
    footnotes: Sequence[str] | None
    info: str | None
    info_link: str | None
    info_link_title: str | None
    search: bool
    page_size: int | Literal["all"] | None
    sortable: bool
    download: bool
    row_shading: bool | int | tuple[int, int] | list[int] | None
    row_lines: bool
    border: bool
    freeze_columns: int
    wrap: bool
    wrap_titles: bool
    format_titles: bool
    show_total_row: bool
    total_label: str
    total_position: Literal["top", "bottom"]
    subtotal_position: Literal["top", "bottom"]
    collapsible: bool
    collapsed: bool | None
    groups_open: bool | None
    group_type: Literal["accordion", "section"] | None
    link: str | None
    width: Length | None
    max_height: Length | None
    order_columns_by_group: bool
    row_numbers: bool
    column_stats: bool
    compact: bool
    empty_message: str | None
    empty_rows: int | None
    default_sort: DefaultSort | None
    row_conditional_colors: str | None
    show_link_column: bool
    select: str | None
    header_color: str | None
    header_font_color: str | None
    total_row_color: str | None
    total_font_color: str | None
    background_color: str | None
    theme: Theme | None
    color_scale: Palette | None


class ColorStop(TypedDict):
    value: float
    color: str


class ColorOptions(TypedDict, total=False):
    color_scale: Palette | None
    color_stops: Sequence[ColorStop] | None
    conditional_colors: str | None
    scale_column: str | None
    scale_mode: Literal["rgb", "lrgb", "lab", "lch", "hsl", "hsv", "hsi", "hcl"] | None
    min: float | None
    max: float | None
    midpoint: float | None


#: Named colour scales — the Evidence presets plus the matplotlib colormaps.
#: Must match ``COLOR_PRESETS`` / ``COLORMAPS`` in ``frontend/src/color.js``
#: (``tests/release/test_color_scales.py`` keeps them in sync).
COLOR_SCALES = (
    # presets
    "green",
    "blue",
    "red",
    "orange",
    "purple",
    "grey",
    "gray",
    # matplotlib: perceptually uniform
    "viridis",
    "magma",
    "plasma",
    "inferno",
    "cividis",
    # matplotlib: sequential
    "blues",
    "reds",
    "greens",
    "greys",
    "oranges",
    "purples",
    "bugn",
    "bupu",
    "gnbu",
    "orrd",
    "pubu",
    "rdpu",
    "ylgn",
    "ylgnbu",
    "ylorbr",
    "ylorrd",
    # matplotlib: diverging
    "rdbu",
    "rdylbu",
    "rdylgn",
    "coolwarm",
    "bwr",
    "spectral",
    "piyg",
    "prgn",
    "brbg",
)


class BarOptions(TypedDict, total=False):
    bar_color: str | None
    bar_color_negative: str | None
    bar_color_column: str | None
    background_color: str | None
    hide_labels: bool | None
    fit_to_data: bool | None
    center: bool | None
    pad: float | str | None
    direction: Literal["left", "right"] | None
    reference: float | None
    reference_color: str | None
    reference_label: str | None


class DeltaOptions(TypedDict, total=False):
    down_is_good: bool | None
    show_symbol: bool | None
    show_value: bool | None
    symbol_position: Literal["left", "right"] | None
    neutral_range: str | float | tuple[float, float] | list[float] | None
    neutral_min: float | None
    neutral_max: float | None
    chip: bool | None


class SparklineOptions(TypedDict, total=False):
    type: Literal["line", "area", "bar"] | None
    x: str | None
    y: str | None
    color: str | None
    fit_to_data: bool | None
    y_fmt: str | None
    width: float | None
    height: float | None


class ChipOptions(TypedDict, total=False):
    min_width: Length | None


class SymbolOptions(TypedDict, total=False):
    symbol: str | None
    shape: Literal["square", "rounded", "circle"] | None
    empty: str | None
    max: int | None
    image: str | None
    color: str | None
    empty_color: str | None
    size: float | None
    gap: float | None


class ImageOptions(TypedDict, total=False):
    height: float | None
    width: float | None
    alt: str | None


class LogoOptions(TypedDict, total=False):
    height: float | None


class ColumnOptions(TypedDict, total=False):
    name: str
    type: str
    title: str | None
    fmt: str | None
    fmt_column: str | None
    relative: Relative | None
    total_fmt: str | None
    subtotal_fmt: str | None
    align: Literal["left", "right", "center"] | None
    wrap: bool | None
    wrap_title: bool | None
    hide: bool
    viz: Literal["bar", "color", "chip", "sparkline", "delta", "symbols"] | None
    red_negatives: bool
    negative_color: str | None
    bracket_negatives: bool | None
    html: bool
    markdown: bool
    link: str | None
    link_label: str | None
    link_new_tab: bool
    image: str | None
    logo: str | None
    column_group: str | Sequence[str] | None
    subcolumn_group: str | None
    info: str | None
    repeat_values: bool | None
    color_options: ColorOptions | None
    bar_options: BarOptions | None
    delta_options: DeltaOptions | None
    sparkline_options: SparklineOptions | None
    chip_options: ChipOptions | None
    symbol_options: SymbolOptions | None
    image_options: ImageOptions | None
    logo_options: LogoOptions | None
    viz_include_subtotals: bool | None
    sort_by: str | None
    highlight: str | None
    null_text: str | None
    blank_below: float | None
    blank_above: float | None
    blank: Callable[[Any], bool] | None
    blank_if: Callable[[Any], bool] | None
    footnote: str | None
    figure_style: FigureStyle | None
    font: str | None
    font_color: str | None
    font_weight: str | None
    font_style: str | None
    rotate_title: Rotation | None
    align_decimals: bool | None
    template: str | None
    template_fmt: Mapping[str, str] | None


TABLE_DEFAULTS: TableOptions = {
    "title": None,
    "subtitle": None,
    "caption": None,
    "null_text": None,
    "stub": None,
    "stub_head": None,
    "footnote_marks": "symbols",
    "all_caps": False,
    "stretch": True,
    "align_decimals": False,
    "group_gap": False,
    "rotate_titles": None,
    "figure_style": None,
    "font_size": None,
    "footnote_column": None,
    "footnotes": None,
    "info": None,
    "info_link": None,
    "info_link_title": None,
    "search": False,
    "page_size": 10,
    "sortable": True,
    "download": True,
    "row_shading": False,
    "row_lines": True,
    "border": True,
    "freeze_columns": 0,
    "wrap": False,
    "wrap_titles": True,
    "format_titles": True,
    "show_total_row": False,
    "total_label": "Total",
    "total_position": "bottom",
    "subtotal_position": "bottom",
    "collapsible": False,
    "collapsed": None,
    "groups_open": None,
    "group_type": None,
    "link": None,
    "width": None,
    "max_height": None,
    "order_columns_by_group": True,
    "row_numbers": False,
    "column_stats": False,
    "compact": False,
    "empty_message": "No records",
    "empty_rows": None,
    "default_sort": None,
    "row_conditional_colors": None,
    "show_link_column": False,
    "select": None,
    "header_color": None,
    "header_font_color": None,
    "total_row_color": None,
    "total_font_color": None,
    "background_color": None,
    "theme": None,
    "color_scale": None,
}


@cache
def _fields(schema: Any) -> dict[str, Any]:
    return get_type_hints(schema)


def settings(**options: Unpack[TableOptions]) -> TableOptions:
    """Collect and validate table-level options, for ``**``-splatting.

    ``EvidentialTable(rows, **settings(title="Sales", page_size=15))`` is the
    same as passing those keywords directly, but a bundle can be reused and
    overridden::

        REPORT = settings(page_size=15, row_shading=True, border=False)
        EvidentialTable(rows, **REPORT)
        EvidentialTable(rows, settings=REPORT, title="This month")
    """
    validate_options(options, TableOptions, "table")
    return cast(TableOptions, dict(options))


def unknown_option(name: str, allowed: Sequence[str], path: str) -> ValueError:
    suggestion = get_close_matches(name, allowed, n=1)
    suffix = f"; did you mean {suggestion[0]!r}?" if suggestion else ""
    return ValueError(f"Unknown {path} option {name!r}{suffix}")


def validate_options(options: Mapping[str, Any], schema: Any, path: str) -> None:
    """Validate known keys and nested values without changing the input."""
    fields = _fields(schema)
    for name, value in options.items():
        if name not in fields:
            raise unknown_option(name, list(fields), path)
        if not _matches(value, fields[name], f"{path}.{name}"):
            raise TypeError(f"{path}.{name} expects {fields[name]}, got {value!r}")
        if name in {"row_shading", "neutral_range"} and isinstance(value, (list, tuple)) and len(value) != 2:
            raise TypeError(f"{path}.{name} expects a pair of values")
    for name in getattr(schema, "__required_keys__", ()):
        if name not in options:
            raise ValueError(f"{path}.{name} is required")


def _matches(value: Any, hint: Any, path: str) -> bool:
    if hint is Any:
        return True
    if hint is type(None):
        return value is None
    if is_typeddict(hint):
        if not isinstance(value, Mapping):
            return False
        validate_options(value, hint, path)
        return True
    origin, args = get_origin(hint), get_args(hint)
    if origin in (Union, types.UnionType):
        return any(_matches(value, alternative, path) for alternative in args)
    if origin is Literal:
        return any(type(value) is type(expected) and value == expected for expected in args)
    if origin is Callable:
        return callable(value)
    if origin in (Sequence, tuple, list):
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            return False
        if origin is tuple:
            return len(value) == len(args) and all(
                _matches(item, item_type, f"{path}[{index}]")
                for index, (item, item_type) in enumerate(zip(value, args, strict=True))
            )
        return all(_matches(item, args[0], f"{path}[{index}]") for index, item in enumerate(value))
    if origin is Mapping:
        return isinstance(value, Mapping) and all(
            _matches(key, args[0], path) and _matches(item, args[1], f"{path}[{key}]") for key, item in value.items()
        )
    if hint is float:
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    if hint in (int, bool):
        return type(value) is hint
    return isinstance(value, hint)
