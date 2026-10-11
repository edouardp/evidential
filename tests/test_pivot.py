from __future__ import annotations

import duckdb
import pytest

from evidence_tables import pivot_table
from evidence_tables.duck import connect


@pytest.fixture()
def sales() -> duckdb.DuckDBPyConnection:
    connection = connect()
    connection.execute(
        """
        CREATE TABLE sales AS SELECT * FROM (VALUES
            ('Toys', 2021, 100.0),
            ('Toys', 2022, 150.0),
            ('Gear', 2021, 200.0),
            ('Gear', 2022, 250.0),
            ('Gear', 2022, 50.0)
        ) AS v(category, year, sales)
        """
    )
    return connection


def test_pivot_columns_and_groups(sales: duckdb.DuckDBPyConnection) -> None:
    table = pivot_table(
        sales,
        "SELECT * FROM sales",
        dimensions=["category"],
        pivots=["year"],
        measures=["sum(sales) AS sales"],
        subtotals=False,
        total=False,
    )
    names = [column["name"] for column in table.columns]
    assert names[0] == "category"
    assert set(names[1:]) == {"sales__2021", "sales__2022", "sales__Total"}

    groups = {column["name"]: column.get("column_group") for column in table.columns}
    assert groups["sales__2021"] == "2021"
    assert groups["sales__2022"] == "2022"
    assert groups["sales__Total"] == "Total"


def test_pivot_values(sales: duckdb.DuckDBPyConnection) -> None:
    table = pivot_table(
        sales,
        "SELECT * FROM sales",
        dimensions=["category"],
        pivots=["year"],
        measures=["sum(sales) AS sales"],
        subtotals=False,
        total=False,
    )
    rows = {row["category"]: row for row in table.rows}
    assert rows["Toys"]["sales__2021"] == 100.0
    assert rows["Toys"]["sales__2022"] == 150.0
    assert rows["Gear"]["sales__2022"] == 300.0  # 250 + 50
    assert rows["Gear"]["sales__Total"] == 500.0


def test_pivot_measures_first(sales: duckdb.DuckDBPyConnection) -> None:
    table = pivot_table(
        sales,
        "SELECT * FROM sales",
        dimensions=["category"],
        pivots=["year"],
        measures=["sum(sales) AS sales", "count(*) AS orders"],
        measures_first=True,
        subtotals=False,
        total=False,
    )
    groups = {column["name"]: column.get("column_group") for column in table.columns}
    assert groups["sales__2021"] == "sales"
    assert groups["orders__2022"] == "orders"
    assert groups["sales__Total"] == "sales"


def test_pivot_total_row(sales: duckdb.DuckDBPyConnection) -> None:
    table = pivot_table(
        sales,
        "SELECT * FROM sales",
        dimensions=["category"],
        pivots=["year"],
        measures=["sum(sales) AS sales"],
    )
    total = next(row for row in table.rows if row["render_type"] == "row_total")
    assert total["category"] == "Total"
    assert total["sales__Total"] == 750.0
    assert table.options["show_total_row"] is True


def test_pivot_requires_pivots(sales: duckdb.DuckDBPyConnection) -> None:
    with pytest.raises(ValueError):
        pivot_table(sales, "SELECT * FROM sales", ["category"], [], ["sum(sales) AS sales"])
