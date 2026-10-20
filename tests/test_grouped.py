from __future__ import annotations

import duckdb
import pytest

from evidential import grouped_table
from evidential.duck import connect


@pytest.fixture()
def sales() -> duckdb.DuckDBPyConnection:
    connection = connect(extensions=())
    connection.execute(
        """
        CREATE TABLE sales AS SELECT * FROM (VALUES
            ('USA', 'NYC', 100.0),
            ('USA', 'LA', 200.0),
            ('USA', 'LA', 50.0),
            ('Canada', 'Toronto', 80.0),
            ('Canada', 'Vancouver', 120.0)
        ) AS v(country, city, revenue)
        """
    )
    return connection


def test_grouped_rows_have_render_metadata(sales: duckdb.DuckDBPyConnection) -> None:
    table = grouped_table(
        sales,
        "SELECT * FROM sales",
        ["country", "city"],
        ["sum(revenue) AS revenue"],
    )
    by_type: dict[str, int] = {}
    for row in table.display_rows:
        by_type[row["render_type"]] = by_type.get(row["render_type"], 0) + 1
    assert by_type == {"cell_data": 4, "row_subtotal": 2, "row_total": 1}

    subtotal = next(row for row in table.display_rows if row["render_type"] == "row_subtotal")
    assert subtotal["__level"] == 1
    assert subtotal["__ancestors"] == []
    assert subtotal["city"] == ""

    detail = next(row for row in table.display_rows if row["render_type"] == "cell_data")
    assert detail["__level"] == 2
    assert detail["__parent_key"] == detail["__ancestors"][0]


def test_grand_total_label_and_value(sales: duckdb.DuckDBPyConnection) -> None:
    table = grouped_table(
        sales,
        "SELECT * FROM sales",
        ["country", "city"],
        ["sum(revenue) AS revenue"],
    )
    total = next(row for row in table.display_rows if row["render_type"] == "row_total")
    assert total["country"] == "Total"
    assert total["revenue"] == 550.0


def test_subtotals_disabled(sales: duckdb.DuckDBPyConnection) -> None:
    table = grouped_table(
        sales,
        "SELECT * FROM sales",
        ["country", "city"],
        ["sum(revenue) AS revenue"],
        subtotals=False,
        total=False,
    )
    assert all(row["render_type"] == "cell_data" for row in table.display_rows)
    assert len(table.display_rows) == 4


def test_subtotal_position_top(sales: duckdb.DuckDBPyConnection) -> None:
    table = grouped_table(
        sales,
        "SELECT * FROM sales",
        ["country", "city"],
        ["sum(revenue) AS revenue"],
        subtotal_position="top",
    )
    types = [row["render_type"] for row in table.display_rows]
    # First row after nothing is a subtotal when placed on top.
    assert types[0] == "row_subtotal"
    assert types[-1] == "row_total"


def test_measure_spec_forms(sales: duckdb.DuckDBPyConnection) -> None:
    table = grouped_table(
        sales,
        "SELECT * FROM sales",
        ["country"],
        ["sum(revenue) AS revenue", ("orders", "count(*)"), {"avg_revenue": "avg(revenue)"}],
        subtotals=False,
    )
    columns = [column["name"] for column in table.columns]
    assert columns == ["country", "revenue", "orders", "avg_revenue"]
    detail = table.display_rows[0]
    assert "revenue" in detail and "orders" in detail and "avg_revenue" in detail


def test_total_measures_override(sales: duckdb.DuckDBPyConnection) -> None:
    table = grouped_table(
        sales,
        "SELECT * FROM sales",
        ["country"],
        ["sum(revenue) AS revenue"],
        total_measures={"revenue": "avg(revenue)"},
    )
    total = next(row for row in table.display_rows if row["render_type"] == "row_total")
    assert total["revenue"] == pytest.approx(110.0)  # avg of 100/200/50/80/120
    detail = next(row for row in table.display_rows if row["render_type"] == "cell_data")
    assert detail["revenue"] in (200.0, 350.0)  # per-country sums


def test_measure_and_dimension_config(sales: duckdb.DuckDBPyConnection) -> None:
    table = grouped_table(
        sales,
        "SELECT * FROM sales",
        ["country"],
        ["sum(revenue) AS revenue"],
        dimension_config={"country": {"title": "Country"}},
        measure_config={"revenue": {"fmt": "usd0", "viz": "bar"}},
    )
    country = next(column for column in table.columns if column["name"] == "country")
    revenue = next(column for column in table.columns if column["name"] == "revenue")
    assert country["title"] == "Country"
    assert revenue["fmt"] == "usd0"
    assert revenue["viz"] == "bar"
    assert revenue["align"] == "right"
