"""The declarative, multi-encoding column builder (ADR-058)."""

from __future__ import annotations

from collections.abc import Mapping

import pytest

from evidential import EvidentialTable, col
from evidential.marks import MarkColumn
from evidential.marks import strip as strip_column

ROWS = [
    {"city": "NYC", "current": 8, "previous": 5, "candidate": "Alpha", "target": 6, "low": 2, "high": 9},
    {"city": "LA", "current": 3, "previous": 7, "candidate": "Beta", "target": 6, "low": 4, "high": 8},
]


def test_single_plain_bar_keeps_the_classic_wire_shape() -> None:
    column = col.bar("current", color="#1d4ed8", fit_to_data=True)
    spec = dict(column)
    assert spec == {
        "name": "current",
        "type": "number",
        "viz": "bar",
        "bar_options": {"bar_color": "#1d4ed8", "fit_to_data": True},
    }
    assert "encodings" not in spec


def test_at_color_is_a_per_row_column() -> None:
    spec = dict(col.bar("current", color="@party_colour"))
    assert spec["bar_options"] == {"bar_color_column": "party_colour"}
    assert "encodings" not in spec


def test_two_bars_emit_ordered_encodings() -> None:
    column = col.bar("current", color="navy", size=0.8).bar("previous", color="#d1d5db", size=0.2)
    encodings = column["encodings"]
    assert [enc["kind"] for enc in encodings] == ["bar", "bar"]
    assert [enc["source"] for enc in encodings] == ["current", "previous"]
    assert encodings[0]["size"] == 0.8 and encodings[1]["size"] == 0.2
    assert "viz" not in dict(column).keys() - {"name", "type"}


def test_bar_owned_label_names_another_field() -> None:
    spec = dict(col.bar("current", label="@candidate", color="#2563eb"))
    encoding = spec["encodings"][0]
    assert encoding["label"] == {"source": "candidate"}
    assert encoding["color"] == "#2563eb"


def test_label_true_labels_the_mark_value_and_fluent_form_positions_it() -> None:
    labelled = col.bar("current", label=True)
    assert labelled["encodings"][0]["label"] == {"value": True}
    positioned = col.bar("current").label(value=True, position="inside_end")
    assert positioned["encodings"][0]["label"] == {"value": True, "position": "inside_end"}
    with pytest.raises(ValueError, match="Unknown label position"):
        col.bar("current").label(position="mid-air")


def test_bar_and_point_share_the_scale() -> None:
    spec = dict(col.bar("current").point("target"))
    assert [enc["kind"] for enc in spec["encodings"]] == ["bar", "point"]
    assert [enc["source"] for enc in spec["encodings"]] == ["current", "target"]


@pytest.mark.parametrize("outline", [False, True, "#334155"])
def test_point_outline_round_trips_for_constructor_and_chained_marks(outline) -> None:
    base = col.bar("current")
    for column in (
        col.point("target", outline=outline),
        base.point("target", outline=outline),
        col.points("samples", outline=outline),
        base.points("samples", outline=outline),
    ):
        table = EvidentialTable([{"current": 3, "target": 4, "samples": [2, 3]}], columns=[column])
        assert table.columns[0]["encodings"][-1]["outline"] == outline
    assert "encodings" not in base


def test_point_outline_defaults_and_validation() -> None:
    assert "outline" not in col.point("target")["encodings"][0]
    for outline in (0, [], ""):
        with pytest.raises(ValueError, match="outline"):
            col.point("target", outline=outline)
    with pytest.raises(ValueError, match="point"):
        col.range("low", "high", outline=False)


def test_range_carries_both_endpoints_and_a_cap() -> None:
    spec = dict(col.range("low", "high", cap="line").point("target"))
    rng, point = spec["encodings"]
    assert (rng["kind"], rng["source"], rng["high"], rng["cap"]) == ("range", "low", "high", "line")
    assert (point["kind"], point["source"]) == ("point", "target")


def test_scale_and_references_are_column_level() -> None:
    spec = dict(col.bar("current").scale(domain=(0, 100), include_zero=True, unit="%").reference_line(55, label="avg"))
    assert spec["scale"] == {"domain": (0, 100), "include_zero": True, "unit": "%"}
    assert spec["references"] == [{"value": 55, "label": "avg"}]


def test_refining_a_label_retains_its_source_and_can_replace_it() -> None:
    base = col.bar("current", label="@candidate")
    positioned = base.label(position="inside_end").label(prefix="→ ")
    assert positioned["encodings"][0]["label"] == {"source": "candidate", "position": "inside_end", "prefix": "→ "}
    assert positioned.label(text="New")["encodings"][0]["label"] == {
        "text": "New",
        "position": "inside_end",
        "prefix": "→ ",
    }
    assert base["encodings"][0]["label"] == {"source": "candidate"}
    assert col.bar("current").bar(label="@candidate")["encodings"][0]["label"] == {"source": "candidate"}


def test_scale_refinement_preserves_domain_and_normalization() -> None:
    base = col.bar("current").scale(domain=(10, 20))
    assert base.scale(axis=True)["scale"] == {"domain": (10, 20), "axis": True}
    assert base.scale(domain="auto", axis=True)["scale"] == {"axis": True}
    assert col.stacked_bar("a", "b", normalize="percent").scale(axis=True)["scale"] == {
        "normalize": "percent",
        "axis": True,
    }


def test_valign_is_not_lost_to_legacy_serialization() -> None:
    assert col.bar("current", valign="top")["encodings"][0]["valign"] == "top"


@pytest.mark.parametrize("domain", [(20, 10), (10, 10), (0, float("inf"))])
def test_scale_requires_finite_increasing_bounds(domain) -> None:
    with pytest.raises(ValueError, match="finite|increasing"):
        col.point("x").scale(domain=domain)


def test_log_domain_validation_survives_fluent_refinement() -> None:
    with pytest.raises(ValueError, match="positive domain"):
        col.point("x").scale(domain=(0, 10)).scale(transform="log")
    with pytest.raises(ValueError, match="positive domain"):
        col.point("x").scale(transform="log").scale(domain=(-1, 10))


def test_label_fit_and_color_options_are_typed_and_preserved() -> None:
    column = col.bar("current").label(value=True, overflow="show", min_width=12, color="red")
    table = EvidentialTable(ROWS, columns=[column])
    assert table.columns[0]["encodings"][0]["label"] == {
        "value": True,
        "overflow": "show",
        "min_width": 12,
        "color": "red",
    }
    with pytest.raises(ValueError, match="overflow"):
        column.label(overflow="clip")
    with pytest.raises(ValueError, match="min_width"):
        column.label(min_width=-1)


def test_bar_refinement_normalizes_color_bindings() -> None:
    base = col.bar("current", color="red", size=0.5)
    assert base.bar(color="@paint")["encodings"][0]["color_column"] == "paint"
    fixed = base.bar(color="@paint").bar(color="blue")["encodings"][0]
    assert fixed["color"] == "blue" and "color_column" not in fixed


@pytest.mark.parametrize(
    "column,data",
    [
        (col.stacked_bar("a", "b"), [{"a": -1, "b": 2}]),
        (col.bar("a", side="left"), [{"a": -1}]),
        (col.point("a").scale(transform="log"), [{"a": 0}]),
        (col.range("a", "b").scale(transform="log"), [{"a": -1, "b": 5}]),
    ],
)
def test_invalid_mark_magnitudes_are_rejected(column, data) -> None:
    with pytest.raises(ValueError, match="nonnegative|positive"):
        EvidentialTable(data, columns=[column])


def test_change_point_strip_requires_a_terminal_bound() -> None:
    data = [{"states": [{"position": 0, "category": "on"}, {"position": 4, "category": "off"}]}]
    with pytest.raises(ValueError, match="terminal bound"):
        EvidentialTable(data, columns=[strip_column("states")])
    table = EvidentialTable(data, columns=[strip_column("states").scale(domain=(0, 10))])
    assert table.columns[0]["scale"]["domain"] == (0, 10)


def test_range_overflow_is_independent_of_its_cap_style() -> None:
    table = EvidentialTable(ROWS, columns=[col.range("low", "high", cap="line", overflow="arrow")])
    assert table.columns[0]["encodings"][0]["overflow"] == "arrow"


def test_two_sided_layout_rejects_an_asymmetric_signed_domain() -> None:
    with pytest.raises(ValueError, match="two-sided scale domain"):
        EvidentialTable([{"a": 10}], columns=[col.bar("a", side="left").scale(domain=(-10, 30))])


def test_callable_bindings_are_unique_per_presentation_and_preserve_source_fields() -> None:
    data = [{"a": 5, "__mark_a_0_color": "original"}]
    columns = [col.bar("a", label=True, color=lambda row: "red"), col.bar("a", label=True, color=lambda row: "blue")]
    table = EvidentialTable(data, columns=columns)
    names = [column["encodings"][0]["color_column"] for column in table.columns]
    assert names[0] != names[1]
    assert [table.rows[0][name] for name in names] == ["red", "blue"]
    assert table.rows[0]["__mark_a_0_color"] == "original"
    table.set_data(data)
    assert [column["encodings"][0]["color_column"] for column in table.columns] == names


def test_incompatible_coordinates_fail_clearly() -> None:
    with pytest.raises(ValueError, match="strip.*share"):
        EvidentialTable([{"states": ["W"], "a": 1}], columns=[strip_column("states").point("a")])
    with pytest.raises(ValueError, match="sparkline.*share"):
        EvidentialTable(ROWS, columns=[col.bar("current").sparkline()])


def test_stack_colors_are_positional_and_length_checked() -> None:
    with pytest.raises(ValueError, match="colors.*segment"):
        col.stacked_bar("a", "b", colors=["red"])


def test_duckdb_structured_sparkline_preserves_order_and_missing_observations() -> None:
    import duckdb

    relation = duckdb.sql("""
        SELECT list({'x': x, 'y': y} ORDER BY x) AS trend
        FROM (VALUES (10, 4), (0, 2), (1, NULL)) AS data(x, y)
    """)
    table = EvidentialTable(relation, columns=[col.sparkline("trend", x="x", y="y")])
    assert table.rows[0]["trend"] == [{"x": 0, "y": 2}, {"x": 1, "y": None}, {"x": 10, "y": 4}]


def test_stacked_bar_is_a_distinct_encoding_with_positional_colours() -> None:
    spec = dict(col.stacked_bar("a", "b", colors=["#111", "#eee"], labels=True))
    kinds = [enc["kind"] for enc in spec["encodings"]]
    assert kinds == ["stacked_bar", "stacked_bar"]
    assert spec["encodings"][0]["color"] == "#111"
    assert spec["encodings"][1]["color"] == "#eee"
    assert spec["encodings"][0]["label"]["value"] is True


def test_mark_column_is_immutable_and_a_mapping() -> None:
    base = col.bar("current", size=0.6)
    chained = base.bar("previous")
    assert isinstance(base, MarkColumn) and isinstance(base, Mapping)
    assert len(base["encodings"]) == 1
    assert len(chained["encodings"]) == 2
    # The classic chain methods still refine a marks column.
    refined = chained.fmt("usd0").align("left")
    assert refined["fmt"] == "usd0" and refined["align"] == "left"
    assert "fmt" not in dict(chained)


def test_marks_column_flows_through_the_table() -> None:
    table = EvidentialTable(
        ROWS,
        columns=[
            col.text("city"),
            col.bar("current", label="@candidate", color="navy").bar("previous", color="#d1d5db", size=0.3),
            col.range("low", "high", cap="line").point("target"),
        ],
    )
    by_name = {column["name"]: column for column in table.columns}
    assert set(by_name) == {"city", "current", "low"}
    assert [enc["source"] for enc in by_name["current"]["encodings"]] == ["current", "previous"]
    assert by_name["current"]["encodings"][0]["label"] == {"source": "candidate"}
    assert by_name["low"]["encodings"][0]["kind"] == "range"


def test_marks_validate_unknown_options() -> None:
    with pytest.raises(TypeError, match="Unknown bar option"):
        col.bar("current", wobble=True)
    with pytest.raises(TypeError, match="field name or a callable"):
        col.bar(42)


def test_scale_rejects_a_bad_domain() -> None:
    with pytest.raises(ValueError, match="domain"):
        col.bar("current").scale(domain=(0, 1, 2))
    with pytest.raises(ValueError, match="auto"):
        col.bar("current").scale(domain="everything")


def test_callable_source_and_colour_become_hidden_columns() -> None:
    rows = [{"yes": 3, "maybe": 1, "party": "A"}, {"yes": 1, "maybe": 2, "party": "B"}]
    table = EvidentialTable(
        rows,
        columns=[
            col.bar(
                lambda r: r["yes"] + r["maybe"], label="@party", color=lambda r: "#f00" if r["party"] == "A" else "#00f"
            )
        ],
    )
    column = table.columns[0]
    encoding = column["encodings"][0]
    # The callee ran Python-side; the wire format only carries field names.
    assert not callable(encoding["source"]) and not callable(encoding["color_column"])
    assert table.rows[0][encoding["source"]] == 4
    assert table.rows[1][encoding["source"]] == 3
    assert table.rows[0][encoding["color_column"]] == "#f00"
    # Hidden helper columns are values in the rows, not displayed columns.
    assert [c["name"] for c in table.columns] == [column["name"]]


def test_callable_point_source_resolves() -> None:
    table = EvidentialTable(
        [{"x": 1, "y": 2}],
        columns=[col.bar("x").point(lambda r: r["x"] + r["y"])],
    )
    source = table.columns[0]["encodings"][1]["source"]
    assert table.rows[0][source] == 3


def test_stacked_bar_percent_normalisation_is_explicit() -> None:
    spec = dict(col.stacked_bar("a", "b", normalize="percent"))
    assert spec["scale"] == {"normalize": "percent"}
    with pytest.raises(ValueError, match="normalize"):
        col.stacked_bar("a", "b", normalize="fraction")


def test_strip_encoding_maps_categories_to_colours() -> None:
    spec = dict(col.strip("form", colors={"W": "green", "D": "grey", "L": "red"}, labels=True, segmented=True))
    assert spec["type"] == "array"
    encoding = spec["encodings"][0]
    assert encoding["kind"] == "strip"
    assert encoding["colors"] == {"W": "green", "D": "grey", "L": "red"}
    assert encoding["strip_labels"] is True
    assert encoding["segmented"] is True


def test_shapes_is_the_repeated_symbol_encoding() -> None:
    assert dict(col.shapes("gold", shape="square", color="gold"))["viz"] == "symbols"


def test_boxplot_carries_a_precomputed_summary() -> None:
    spec = dict(col.boxplot("lo", "q1", "med", "q3", "hi", outliers="outs", whisker="iqr", color="#111"))
    encoding = spec["encodings"][0]
    assert encoding["kind"] == "boxplot"
    assert encoding["parts"] == {"minimum": "lo", "q1": "q1", "median": "med", "q3": "q3", "maximum": "hi"}
    assert encoding["outliers"] == "outs"
    assert encoding["whisker"] == "iqr"
    assert encoding["source"] == "med"


def test_boxplot_rejects_an_unknown_whisker() -> None:
    with pytest.raises(ValueError, match="whisker"):
        col.boxplot("a", "b", "c", "d", "e", whisker="tukey")
    with pytest.raises(TypeError, match="Unknown boxplot option"):
        col.boxplot("a", "b", "c", "d", "e", wobble=True)


def test_boxplot_callable_parts_become_hidden_columns() -> None:
    table = EvidentialTable(
        [{"lo": 1, "q1": 2, "med": 3, "q3": 4, "hi": 5}],
        columns=[col.boxplot(lambda r: r["lo"], "q1", "med", "q3", "hi")],
    )
    parts = table.columns[0]["encodings"][0]["parts"]
    assert table.rows[0][parts["minimum"]] == 1


def test_diverging_stack_marks_the_pivot() -> None:
    spec = dict(
        col.stacked_bar(
            "strongly_disagree", "disagree", "neutral", "agree", "strongly_agree", diverge_at="neutral", neutral="split"
        )
    )
    first = spec["encodings"][0]
    assert first["diverge_at"] == "neutral" and first["neutral"] == "split"
    with pytest.raises(ValueError, match="diverge_at"):
        col.stacked_bar("a", "b", diverge_at="c")


def test_distribution_is_a_precomputed_density_band() -> None:
    spec = dict(col.distribution("density", x="seats", y="share", color="#111"))
    encoding = spec["encodings"][0]
    assert spec["type"] == "array"
    assert (encoding["kind"], encoding["x"], encoding["y"], encoding["style"]) == (
        "distribution",
        "seats",
        "share",
        "band",
    )
    assert encoding["color"] == "#111"
    with pytest.raises(ValueError, match="style"):
        col.distribution("d", style="violin")


def test_log_scale_is_explicit_and_rejects_nonpositive_domains() -> None:
    spec = dict(col.range("lo", "hi").point("est").scale(domain=(1, 100), transform="log"))
    assert spec["scale"] == {"domain": (1, 100), "transform": "log"}
    with pytest.raises(ValueError, match="log scale needs a positive domain"):
        col.point("x").scale(domain=(0, 100), transform="log")
    with pytest.raises(ValueError, match="transform"):
        col.point("x").scale(transform="symlog")


def test_reference_band_is_a_column_wide_zone() -> None:
    spec = dict(col.point("est").reference_band(0.8, 1.25, label="Equivalence"))
    assert spec["references"] == [{"value": 0.8, "high": 1.25, "label": "Equivalence"}]
    with pytest.raises(ValueError, match="high > low"):
        col.point("est").reference_band(2, 1)


def test_points_draws_an_array_as_a_marker_per_observation() -> None:
    spec = dict(col.points("observations", size=5, color="#111"))
    assert spec["type"] == "array"
    encoding = spec["encodings"][0]
    assert (encoding["kind"], encoding["source"], encoding["size"], encoding["color"]) == (
        "points",
        "observations",
        5,
        "#111",
    )
    table = EvidentialTable([{"x": 1, "observations": [1, 2, 3]}], columns=[col.bar("x").points("observations")])
    assert [enc["kind"] for enc in table.columns[0]["encodings"]] == ["bar", "points"]


def test_scale_axis_gridlines_and_position() -> None:
    spec = dict(col.bar("x").scale(domain=(0, 100), axis=True, axis_position="bottom", gridlines=True))
    assert spec["scale"] == {
        "domain": (0, 100),
        "axis": True,
        "axis_position": "bottom",
        "gridlines": True,
    }
    with pytest.raises(ValueError, match="axis_position"):
        col.bar("x").scale(axis_position="side")


def test_mark_valign_places_marks_vertically() -> None:
    spec = dict(col.bar("x", valign="top").bar("y", valign="bottom").point("z", valign="center"))
    assert [enc["valign"] for enc in spec["encodings"]] == ["top", "bottom", "center"]


def test_label_prefix_suffix_and_align() -> None:
    spec = dict(col.bar("x").label(value=True, prefix="$", suffix="m", align="begin"))
    assert spec["encodings"][0]["label"] == {"value": True, "prefix": "$", "suffix": "m", "align": "begin"}
    mapping = dict(col.point("y", label={"source": "name", "prefix": "→ "}))
    assert mapping["encodings"][0]["label"] == {"source": "name", "prefix": "→ "}
    with pytest.raises(ValueError, match="label align"):
        col.bar("x").label(align="middle")


def test_stacked_bar_label_align() -> None:
    spec = dict(col.stacked_bar("a", "b", labels=True, label_align="begin"))
    assert spec["encodings"][0]["label"]["align"] == "begin"
    with pytest.raises(ValueError, match="label align"):
        col.stacked_bar("a", labels=True, label_align="left")


def test_stacked_bar_percent_labels_and_thickness() -> None:
    spec = dict(col.stacked_bar("a", "b", labels="percent", label_align="begin", size=0.5))
    first = spec["encodings"][0]
    assert first["label"] == {"value": True, "position": "inside_end", "align": "begin", "share": True}
    assert [enc["size"] for enc in spec["encodings"]] == [0.5, 0.5]
    with pytest.raises(ValueError, match="labels is True, False or 'percent'"):
        col.stacked_bar("a", labels="count")
    with pytest.raises(ValueError, match="size is a fraction"):
        col.stacked_bar("a", size=2)


def test_range_can_be_a_filled_band() -> None:
    spec = dict(col.range("low", "high", fill=True, color="#8b5cf6").point("estimate"))
    rng = spec["encodings"][0]
    assert rng["fill"] is True and rng["kind"] == "range" and rng["color"] == "#8b5cf6"
