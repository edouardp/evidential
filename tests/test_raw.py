"""Unformatted source snapshots are independent of presentation and live queries."""

import datetime as dt
from decimal import Decimal

import duckdb
import marimo as mo
import pandas as pd
import pyarrow as pa
import pytest

from evidential import (
    EvidentialTable,
    LiveEvidentialTable,
    col,
    comparison_table,
    grouped_records,
    grouped_table,
    pivot_table,
    query_table,
    rows,
    section_row,
    simple_table,
)
from evidential.rules import cells_body, text_transform


def test_raw_precedes_transforms_blanking_and_generated_marks_and_includes_hidden_fields():
    source = [{"name": "Alpha", "amount": 1234.5, "secret": "kept", "missing": None}]
    table = EvidentialTable(
        source,
        columns=[
            col.text("name"),
            col.number("amount").fmt("usd0").blank(lambda row: True),
            col.text("secret").hide(),
            col.bar(lambda row: len(row["name"])),
        ],
        rules=[text_transform(cells_body("name"), str.upper)],
        search=True,
        page_size=1,
        default_sort={"column": "amount", "direction": "desc"},
    )
    assert table.rows[0]["amount"] is None
    assert table.rows[0]["name"] == "ALPHA"
    assert table.raw == source
    table.set_column("name", title="Renamed")
    table.update_options(page_size=20)
    assert table.raw == source


def test_raw_is_deeply_detached_from_the_source_widget_and_other_snapshots():
    source = [{"name": "Alpha", "series": [{"year": 2023, "value": 1.5}]}]
    table = EvidentialTable(source)
    snapshot = table.raw
    snapshot[0]["series"][0]["value"] = 999
    snapshot[0]["extra"] = "local"
    snapshot.append({"name": "Beta"})
    assert table.raw == source
    assert table.rows == source
    table.set_data([{"name": "Beta", "series": []}])
    assert table.raw == [{"name": "Beta", "series": []}]
    assert snapshot[0]["series"][0]["value"] == 999


@pytest.mark.parametrize("container", [list, pd.DataFrame, pa.Table.from_pylist])
def test_raw_has_one_record_format_for_all_input_containers(container):
    source = [{"date": dt.date(2023, 1, 1), "amount": Decimal("1234.50"), "missing": None}]
    table = EvidentialTable(container(source))
    assert table.raw == [{"date": "2023-01-01", "amount": 1234.5, "missing": None}]
    assert EvidentialTable(rows=source).raw == table.raw


def test_raw_excludes_synthetic_rows_and_layout_summaries():
    source = [{"group": "A", "value": 10}, {"group": "B", "value": 20}]
    table = EvidentialTable(source, row_layout=rows.group_by("group").section().summary().grand_summary())
    assert len(table.display_rows) > len(source)
    assert table.raw == source
    table.set_data(rows=[section_row("Section"), *source], row_layout=None)
    assert table.raw == source
    assert EvidentialTable().raw == []


def test_live_raw_is_the_latest_successful_query_without_rerunning():
    with duckdb.connect() as connection:
        connection.execute("CREATE SEQUENCE runs")
        table = LiveEvidentialTable(
            connection,
            "SELECT nextval('runs') AS run, {amount} AS amount",
            auto_run=False,
            columns=[col.number("amount").fmt("usd0")],
        )
        assert table.raw == []
        table.set_controls(amount=1.5)
        first = table.raw
        assert first == table.raw == [{"run": 1, "amount": 1.5}]
        table.set_controls(amount=2.5)
        assert table.raw == [{"run": 2, "amount": 2.5}]
        assert first == [{"run": 1, "amount": 1.5}]
        with pytest.raises(duckdb.Error):
            table.run(sql="SELECT missing_column")
        assert table.raw == [{"run": 2, "amount": 2.5}]
        with pytest.raises(ValueError):
            table.set_data([{"amount": -1}], columns=[col.bar("amount", side="left")])
        assert table.raw == [{"run": 2, "amount": 2.5}]


def test_raw_is_available_on_all_table_helpers_and_displays_in_marimos_grid():
    with duckdb.connect() as connection:
        sql = """SELECT * FROM (VALUES
            ('A', DATE '2022-01-01', 100.0), ('A', DATE '2023-01-01', 150.0)
        ) t(category, date, amount)"""
        tables = [
            EvidentialTable.from_duckdb(connection, sql),
            simple_table(connection, sql),
            query_table(connection, sql),
            grouped_records([{"category": "A", "amount": 150}], group_by="category"),
            grouped_table(connection, sql, dimensions=["category"], measures=["sum(amount) AS amount"]),
            pivot_table(connection, sql, dimensions=["category"], pivots=["date"], measures=["sum(amount) AS amount"]),
            comparison_table(
                connection, sql, dimensions=["category"], date_column="date", measures=["sum(amount) AS amount"]
            ),
        ]
        for table in tables:
            snapshot = table.raw
            assert snapshot
            assert all(row.get("render_type") in (None, "cell_data") for row in snapshot)
            grid = mo.ui.table(snapshot, selection=None, pagination=True)
            assert grid.data == snapshot
            assert grid._repr_html_()
