from __future__ import annotations

import json
from decimal import Decimal

from evidential import (
    EvidentialTable,
    cells_body,
    cols_merge_range,
    sub_missing,
    sub_small_vals,
    sub_values,
    tab_format,
    tab_style,
    text_transform,
)


def test_style_rule_resolves_rows() -> None:
    table = EvidentialTable(
        [{"city": "NYC", "trips": 12000}, {"city": "LA", "trips": 8000}],
        rules=[
            tab_style(
                cells_body(columns=["trips"], rows=lambda row: row["trips"] > 10000),
                color="#b91c1c",
                font_weight="600",
            )
        ],
    )
    rules = table.options["rules"]
    assert rules[0]["rows"] == [0]
    assert rules[0]["style"] == {"color": "#b91c1c", "font-weight": "600"}


def test_format_rule_by_index() -> None:
    table = EvidentialTable(
        [{"a": 1}, {"a": 2}],
        rules=[tab_format(cells_body(columns="a", rows=[1]), "usd0")],
    )
    assert table.options["rules"][0]["fmt"] == "usd0"
    assert table.options["rules"][0]["rows"] == [1]


def test_text_transform_applied() -> None:
    table = EvidentialTable(
        [{"name": "alpha"}, {"name": "beta"}],
        rules=[text_transform(cells_body(columns="name"), str.upper)],
    )
    assert [row["name"] for row in table.rows] == ["ALPHA", "BETA"]


def test_rows_get_stable_id_when_rules_present() -> None:
    table = EvidentialTable([{"a": 1}, {"a": 2}], rules=[tab_format(cells_body("a"), "id")])
    assert [row["__row_id"] for row in table.rows] == [0, 1]


def test_sub_small_vals_rule() -> None:
    table = EvidentialTable(
        [{"v": 0.001}, {"v": 10}],
        rules=[sub_small_vals(columns="v", threshold=0.01, small_text="small")],
    )
    rule = table.options["rules"][0]
    assert rule["type"] == "substitute"
    assert rule["kind"] == "small"
    assert rule["threshold"] == 0.01
    assert rule["text"] == "small"


def test_sub_missing_and_values() -> None:
    table = EvidentialTable(
        [{"v": None}, {"v": 0}, {"v": 7}],
        rules=[sub_missing(columns="v", missing_text="n/a"), sub_values(columns="v", values=[0], replacement="-")],
    )
    kinds = {rule["kind"] for rule in table.options["rules"]}
    assert kinds == {"missing", "values"}


def test_cols_merge_range_creates_template_column() -> None:
    table = EvidentialTable(
        [{"low": 1, "high": 2}],
        column_config={"range": cols_merge_range("low", "high", fmt="num0")},
    )
    column = next(column for column in table.columns if column["name"] == "range")
    assert column["template"] == "{low}\u2013{high}"
    assert column["template_fmt"] == {"low": "num0", "high": "num0"}


def test_footnote_marks_and_all_caps() -> None:
    table = EvidentialTable([{"a": 1}], footnote_marks="letters", all_caps=True)
    assert table.options["footnote_marks"] == "letters"
    assert table.options["all_caps"] is True


def test_stretch_and_align_decimals_options() -> None:
    table = EvidentialTable([{"a": 1.5}], stretch=False, align_decimals=True)
    assert table.options["stretch"] is False
    assert table.options["align_decimals"] is True


def test_rotate_titles_option() -> None:
    table = EvidentialTable([{"a": 1}], rotate_titles="vertical")
    assert table.options["rotate_titles"] == "vertical"
    oblique = EvidentialTable([{"a": 1}], rotate_titles=-45)
    assert oblique.options["rotate_titles"] == -45


def test_figure_style_option() -> None:
    table = EvidentialTable([{"a": 1}], figure_style="lining-tabular")
    assert table.options["figure_style"] == "lining-tabular"


def test_generator_rules_apply_on_initial_render() -> None:
    table = EvidentialTable([{"a": 1}], rules=(rule for rule in [tab_format(cells_body("a"), "usd0")]))
    assert table.options["rules"][0]["fmt"] == "usd0"
    assert table.rows[0]["__row_id"] == 0


def test_transform_results_are_normalized_for_json() -> None:
    table = EvidentialTable([{"a": 1}], rules=[text_transform(cells_body("a"), lambda _: Decimal("1.5"))])
    assert table.rows[0]["a"] == 1.5
    json.dumps(table.rows, allow_nan=False)
