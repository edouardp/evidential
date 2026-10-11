from __future__ import annotations

import datetime as dt
from decimal import Decimal

import pytest

from evidence_tables import EvidenceTable, make_column
from evidence_tables.duck import connect


def test_from_records_infers_columns() -> None:
    table = EvidenceTable(
        [
            {"city": "NYC", "trips": 120, "revenue": 4200.5, "when": dt.date(2024, 1, 1)},
            {"city": "LA", "trips": 90, "revenue": 3100.0, "when": dt.date(2024, 1, 2)},
        ]
    )
    types = {column["name"]: column["type"] for column in table.columns}
    assert types == {"city": "string", "trips": "number", "revenue": "number", "when": "date"}
    # Dates are serialized to ISO strings for JSON transport.
    assert table.rows[0]["when"] == "2024-01-01"


def test_column_config_overrides() -> None:
    table = EvidenceTable(
        [{"revenue": 4200.5}],
        column_config={
            "revenue": {"fmt": "usd0", "viz": "bar", "align": "right"},
        },
    )
    column = table.columns[0]
    assert column["fmt"] == "usd0"
    assert column["viz"] == "bar"
    assert column["align"] == "right"


def test_table_options_round_trip() -> None:
    table = EvidenceTable([{"a": 1}], title="Hello", search=True, page_size=25)
    assert table.options["title"] == "Hello"
    assert table.options["search"] is True
    assert table.options["page_size"] == 25
    table.update_options(page_size=5)
    assert table.options["page_size"] == 5


def test_set_column_appends_and_updates() -> None:
    table = EvidenceTable([{"a": 1}])
    table.set_column("a", fmt="num0")
    table.set_column("b", type="number", viz="color")
    names = [column["name"] for column in table.columns]
    assert names == ["a", "b"]
    assert table.columns[1]["viz"] == "color"


def test_jsonify_handles_decimal_and_nan() -> None:
    table = EvidenceTable([{"x": Decimal("1.5"), "y": float("nan")}])
    assert table.rows[0]["x"] == 1.5
    assert table.rows[0]["y"] is None


def test_from_duckdb_relation() -> None:
    connection = connect()
    connection.execute("CREATE TABLE t AS SELECT 1 AS a, 'x' AS b")
    table = EvidenceTable.from_duckdb(connection, "SELECT * FROM t")
    assert table.rows == [{"a": 1, "b": "x"}]
    types = {column["name"]: column["type"] for column in table.columns}
    assert types == {"a": "number", "b": "string"}


def test_column_groups_assign_group_without_reordering() -> None:
    table = EvidenceTable(
        [{"month": "Jan", "cc": 1, "cash": 2, "other": 3}],
        column_groups={"Payment type": ["cc", "cash"]},
    )
    names = [column["name"] for column in table.columns]
    assert names == ["month", "cc", "cash", "other"]
    groups = {column["name"]: column.get("column_group") for column in table.columns}
    assert groups["cc"] == "Payment type"
    assert groups["cash"] == "Payment type"
    assert groups["month"] is None


def test_content_type_shorthand_maps_to_viz() -> None:
    table = EvidenceTable(
        [{"trend": [1, 2, 3]}],
        columns=[{"name": "trend", "content_type": "sparkbar"}],
    )
    column = table.columns[0]
    assert column["viz"] == "sparkline"
    assert column["sparkline_options"]["type"] == "bar"


def test_camelcase_column_aliases() -> None:
    table = EvidenceTable(
        [{"x": 1, "url": "https://example.com"}],
        columns=[
            {"name": "url", "contentType": "link"},
            {"name": "x", "colGroup": "Group A", "redNegatives": True, "description": "hint"},
        ],
    )
    url = next(column for column in table.columns if column["name"] == "url")
    assert url["link"] == "url"
    x = next(column for column in table.columns if column["name"] == "x")
    assert x["column_group"] == "Group A"
    assert x["red_negatives"] is True
    assert x["info"] == "hint"


def test_new_table_options_round_trip() -> None:
    table = EvidenceTable(
        [{"a": 1}],
        row_numbers=True,
        compact=True,
        empty_message="Nothing here",
        default_sort={"column": "a", "direction": "asc"},
        row_conditional_colors="tint",
        header_color="#eeeeee",
    )
    assert table.options["row_numbers"] is True
    assert table.options["compact"] is True
    assert table.options["empty_message"] == "Nothing here"
    assert table.options["default_sort"] == {"column": "a", "direction": "asc"}
    assert table.options["row_conditional_colors"] == "tint"
    assert table.options["header_color"] == "#eeeeee"


def test_show_link_column() -> None:
    rows = [{"name": "A", "url": "https://example.com"}]
    hidden = EvidenceTable(rows, link="url")
    url = next(column for column in hidden.columns if column["name"] == "url")
    assert url.get("hide") is True

    shown = EvidenceTable(rows, link="url", show_link_column=True)
    url = next(column for column in shown.columns if column["name"] == "url")
    assert not url.get("hide")


def test_make_column_defaults() -> None:
    column = make_column("trip_distance", type="number", fmt="num1")
    assert column["name"] == "trip_distance"
    assert column["hide"] is False
    assert column["type"] == "number"


@pytest.mark.parametrize("widget", [EvidenceTable([{"a": 1}])])
def test_widget_has_static_assets(widget: EvidenceTable) -> None:
    from importlib.resources import files

    static = files("evidence_tables").joinpath("static")
    assert static.joinpath("table.js").is_file()
    assert static.joinpath("table.css").is_file()
