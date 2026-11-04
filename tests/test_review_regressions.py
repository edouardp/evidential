"""Public-boundary regressions found during the repository review."""

from unittest.mock import patch

import duckdb
import pytest

from evidential import EvidentialTable, LiveEvidentialTable, col, comparison_table, grouped_table, pivot_table
from evidential.marks import normalize_encoding


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


def test_group_labels_own_their_mutable_path():
    path = ["Company", "Sales"]
    group = col.group(path, [col.number("value")])
    path.append("Changed")
    group.label.append("Also changed")
    assert group.label == ["Company", "Sales"]


def test_raw_encodings_are_normalized_once_during_column_assembly():
    with patch("evidential.marks.normalize_encoding", wraps=normalize_encoding) as normalize:
        table = EvidentialTable(
            [{"x": 1}],
            columns=[
                {
                    "name": "x",
                    "type": "number",
                    "encodings": [
                        {"kind": "point", "source": "x"},
                    ],
                }
            ],
        )
    assert table.columns[0]["encodings"][0]["kind"] == "point"
    assert normalize.call_count == 1


@pytest.mark.parametrize(
    "options",
    [
        {"format": "num2", "redNegatives": True},
        {"contentType": "chip", "color_scale": "viridis", "color_min": 0, "color_max": 2},
        {"contentType": "bar", "barColor": "@paint", "hideLabels": False},
    ],
)
def test_alias_precedence_matches_constructor_updates_and_data_refresh(options):
    records = [{"value": 1, "paint": "red"}]
    direct = EvidentialTable(records, columns=[col.auto("value")], column_config={"value": options})
    updated = EvidentialTable(records, columns=[col.auto("value")])
    updated.set_column("value", **options)
    assert updated.columns == direct.columns
    updated.set_data(records)
    assert updated.columns == direct.columns


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
