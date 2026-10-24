"""Equivalent public entry points must prepare the same configuration and data."""

import json
from typing import Self, get_type_hints

import pytest

from evidential import EvidentialTable, col, rows
from evidential._column import Column
from evidential.rules import cells_body, cols_merge, cols_merge_n_pct, cols_merge_range, tab_format, text_transform


@pytest.mark.parametrize(
    "factory",
    [
        col.number,
        col.integer,
        col.percent,
        col.currency,
        col.date,
        col.text,
        col.bar,
        col.point,
        col.points,
        col.strip,
        col.distribution,
    ],
)
def test_common_format_alias(factory):
    assert factory("x", format="num2").to_config()["fmt"] == "num2"
    assert factory("x", fmt="num2").to_config()["fmt"] == "num2"
    with pytest.raises(ValueError, match="format.*fmt|fmt.*format"):
        factory("x", format="num2", fmt="num1")


def test_serialization_normalizes_and_is_round_trippable():
    for column in (col.point("x"), col.number("x", contentType="bar")):
        config = column.to_config()
        assert config["name"] == "x"
        assert (
            EvidentialTable([{"x": 1}], columns=[config]).columns
            == EvidentialTable([{"x": 1}], columns=[column]).columns
        )
    with pytest.raises((TypeError, ValueError)):
        col.point("x").align("diagonal").to_config()


def test_blank_and_transform_order_is_identical_for_all_entry_points():
    source = [{"x": -1}, {"x": 2}]
    columns = [col.number("x").blank(lambda x: x < 0), col.point(lambda row: row["x"], title="derived")]
    table = EvidentialTable(
        source, columns=columns, rules=[text_transform(cells_body("x"), lambda x: None if x is None else x * 10)]
    )
    original = table.rows
    assert original[0]["x"] is None
    field = table.columns[1]["encodings"][0]["source"]
    assert original[1][field] == 20
    table.set_data(source)
    assert table.rows == original
    table.set_column("x", format="num2")
    assert table.rows == original  # transforms must not run twice


def test_mutations_resolve_callables_and_options_atomically():
    table = EvidentialTable([{"x": 2}], groups_open=True)
    table.set_column("x", encodings=[{"kind": "point", "source": lambda row: row["x"] * 3}])
    field = table.columns[0]["encodings"][0]["source"]
    assert table.rows[0][field] == 6
    json.dumps(table.columns)
    table.set_data([{"x": 4}])
    assert table.rows[0][field] == 12
    table.update_options(groups_open=False)
    assert table.options["collapsed"] is True
    before = table.columns
    with pytest.raises((TypeError, ValueError)):
        table.set_column("x", encodings=[{"kind": "point", "source": "x", "size": -1}])
    assert table.columns == before


def test_refinement_preserves_options_and_label_noop():
    classic = col.number("x").bar(color="blue", center=True).bar(pad=4)
    assert classic["bar_options"] == {"bar_color": "blue", "center": True, "pad": 4}
    assert col.number("x").color(scale="blue", min=0).color(max=10)["color_options"] == {
        "color_scale": "blue",
        "min": 0,
        "max": 10,
    }
    labelled = col.point("x", label=True)
    assert dict(labelled.label()) == dict(labelled)
    assert not labelled.label(False)["encodings"][0].get("label")
    with pytest.raises(ValueError, match="bar"):
        col.bar("x").point("y").bar(color="red")
    with pytest.raises(ValueError, match="bar"):
        col.bar("x").color(scale="green").bar(color="red")
    assert col.bar("x").label(False).label(True)["encodings"][0]["hide_labels"] is False


def test_negative_colors_and_height_aliases_are_shared():
    for column in (
        col.bar("x", negative_color="@ink", height=0.6),
        col.bar("x").bar(color_negative="@ink", height=0.6),
    ):
        encoding = column["encodings"][0]
        assert encoding["color_negative_column"] == "ink"
        assert encoding["size"] == 0.6
    assert col.boxplot("lo", "q1", "x", "q3", "hi", color="@ink")["encodings"][0]["color_column"] == "ink"
    assert col.bar("x").color(scale="green").to_config()["viz"] == "color"
    assert "encodings" not in col.bar("x").color(scale="green").to_config()


@pytest.mark.parametrize(
    "build",
    [
        lambda: col.range("x"),
        lambda: col.bar("x", size=-1),
        lambda: col.point("x", size=-1),
        lambda: col.point("x", center=True),
        lambda: col.point("x", label={"value": True, "position": "mid-air"}),
        lambda: col.stacked_bar("x", bogus=True),
    ],
)
def test_invalid_mark_options_fail_at_the_boundary(build):
    with pytest.raises((ValueError, TypeError)):
        build().to_config()


def test_all_mark_factories_share_metadata_and_composition():
    assert col.stacked_bar("x", "y", format="num2", align="left")["fmt"] == "num2"
    assert col.boxplot("lo", "q1", "x", "q3", "hi", format="num2", align="left")["fmt"] == "num2"
    column = col.point("x").distribution("curve").boxplot("lo", "q1", "x", "q3", "hi").stacked_bar("a", "b")
    assert [enc["kind"] for enc in column["encodings"]] == [
        "point",
        "distribution",
        "boxplot",
        "stacked_bar",
        "stacked_bar",
    ]
    assert col.strip("sequence").strip("other")["encodings"][-1]["source"] == "other"  # noqa: B005
    chained = col.point("x").bar("y", format="num2", align="left", label_options={"prefix": "$"})
    assert chained["fmt"] == "num2" and chained["align"] == "left"
    assert chained["encodings"][-1]["label"]["prefix"] == "$"


def test_format_rule_alias_and_subclass_typing():
    assert tab_format(cells_body("x"), format="num2") == tab_format(cells_body("x"), fmt="num2")
    assert get_type_hints(Column.title)["return"] is Self


def test_format_aliases_extend_to_summaries_merges_and_column_references():
    assert rows.aggregate("sum", format="num2") == rows.aggregate("sum", fmt="num2")
    assert cols_merge("{x}", template_format={"x": "num2"}) == cols_merge("{x}", template_fmt={"x": "num2"})
    assert cols_merge_range("lo", "hi", format="num2")["template_fmt"] == {"lo": "num2", "hi": "num2"}
    assert cols_merge_n_pct("n", "share", format="num0", pct_format="pct2")["template_fmt"] == {
        "n": "num0",
        "share": "pct2",
    }
    column = col.number("x").format_column("@code").total_format("num1").subtotal_format("num2")
    assert column.to_config()["fmt_column"] == "code"
    assert column.to_config()["total_fmt"] == "num1"
    with pytest.raises(ValueError, match="disagree"):
        cols_merge("{x}", template_format={"x": "num0"}, template_fmt={"x": "num2"})
    with pytest.raises(ValueError, match="disagree"):
        cols_merge_n_pct("n", "share", pct_format="pct2", pct_fmt="pct1")
    assert "share" not in cols_merge_n_pct("n", "share", pct_format=None, format="num0")["template_fmt"]


def test_raw_encodings_use_builder_validation_and_callable_failures_are_transactional():
    table = EvidentialTable([{"x": 2}])
    with pytest.raises(ValueError, match="position"):
        table.set_column("x", encodings=[{"kind": "point", "source": "x", "label": {"position": "mid-air"}}])
    with pytest.raises(ZeroDivisionError):
        table.set_column("x", encodings=[{"kind": "point", "source": lambda row: 1 / 0}])
    assert table.rows == [{"x": 2}]
    table.set_data([{"x": 4}])
    assert "encodings" not in table.columns[0]
    assert table.rows == [{"x": 4}]


def test_update_options_reuses_link_visibility_precedence():
    table = EvidentialTable([{"x": 2, "url": "https://example.com"}], link="url")
    assert table.columns[1]["hide"] is True
    table.update_options(show_link_column=True)
    assert not table.columns[1].get("hide")
    table.set_data([{"x": 4, "url": "https://example.com"}])
    assert not table.columns[1].get("hide")
    table.update_options(groups_open=False, collapsed=False)
    assert table.options["collapsed"] is False


def test_options_do_not_reexecute_callbacks_and_source_snapshots_are_isolated():
    calls = []

    def transform(values):
        calls.append(True)
        values.append(3)
        return values

    table = EvidentialTable([{"samples": [1, 2]}], rules=[text_transform(cells_body("samples"), transform)])
    assert table.rows[0]["samples"] == [1, 2, 3]
    table.update_options(font_size=12)
    assert len(calls) == 1
    table.set_column("samples", title="Samples")
    assert table.rows[0]["samples"] == [1, 2, 3]
