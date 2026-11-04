"""Public-boundary regressions found during the repository review."""

import duckdb
import pytest

from evidential import LiveEvidentialTable, col, comparison_table, grouped_table, pivot_table


def test_columns_own_nested_configuration_and_do_not_expose_shared_mutable_values():
    palette = ["red", "blue"]
    base = col.number("value").color(scale=palette)
    derived = base.title("Other")
    palette[0] = "black"
    assert base["color_options"]["color_scale"] == ["red", "blue"]
    derived["color_options"]["min"] = -999
    assert "min" not in base["color_options"]
    exported = dict(base)
    exported["color_options"]["color_scale"].append("green")
    assert len(base["color_options"]["color_scale"]) == 2


@pytest.mark.parametrize("dimension", ["order group", "select", 'quoted"name'])
@pytest.mark.parametrize("kind", ["grouped", "pivot", "comparison"])
def test_query_helpers_quote_dimension_and_measure_identifiers(dimension, kind):
    quoted = '"' + dimension.replace('"', '""') + '"'
    sql = f"SELECT 'A' AS {quoted}, 10 AS sales, 2024 AS year, DATE '2024-01-01' AS day"
    with duckdb.connect() as connection:
        arguments = (connection, sql, [dimension])
        measures = [("sales total", "sum(sales)")]
        if kind == "grouped":
            table = grouped_table(*arguments, measures=measures)
        elif kind == "pivot":
            table = pivot_table(*arguments, pivots=["year"], measures=measures)
        else:
            table = comparison_table(*arguments, measures=measures, date_column="day")
        assert table.raw[0][dimension] == "A"


@pytest.mark.parametrize(
    "sql, expected",
    [
        ("SELECT E'can\\'t use {name}' AS text, {p} AS p", {"text": "can't use {name}", "p": 1}),
        ("SELECT {p} AS p /* outer /* inner */ {name} */", {"p": 1}),
    ],
)
def test_live_binding_respects_escaped_strings_and_nested_comments(sql, expected):
    with duckdb.connect() as connection:
        live = LiveEvidentialTable(connection, sql, params={"p": 1})
        assert live.raw == [expected]
        live.close()
