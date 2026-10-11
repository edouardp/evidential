from __future__ import annotations

import duckdb
import pytest

from evidence_tables import comparison_table
from evidence_tables.duck import connect


@pytest.fixture()
def orders() -> duckdb.DuckDBPyConnection:
    connection = connect()
    connection.execute(
        """
        CREATE TABLE orders AS SELECT * FROM (VALUES
            ('A', DATE '2020-06-01', 100.0),
            ('A', DATE '2021-06-01', 150.0),
            ('B', DATE '2020-06-01', 200.0),
            ('B', DATE '2021-06-01', 100.0)
        ) AS v(category, order_date, sales)
        """
    )
    return connection


def test_prior_year_values(orders: duckdb.DuckDBPyConnection) -> None:
    table = comparison_table(
        orders,
        "SELECT category, order_date, sales FROM orders",
        dimensions=["category"],
        measures=["sum(sales) AS sales"],
        date_column="order_date",
        compare_vs="prior year",
    )
    rows = {row["category"]: row for row in table.rows}
    assert rows["A"]["sales"] == 150.0
    assert rows["A"]["sales_prior"] == 100.0
    assert rows["A"]["sales_delta"] == 50.0
    assert rows["A"]["sales_pct"] == pytest.approx(0.5)
    assert rows["B"]["sales_delta"] == -100.0
    assert rows["B"]["sales_pct"] == pytest.approx(-0.5)


def test_comparison_column_config(orders: duckdb.DuckDBPyConnection) -> None:
    table = comparison_table(
        orders,
        "SELECT category, order_date, sales FROM orders",
        dimensions=["category"],
        measures=["sum(sales) AS sales"],
        date_column="order_date",
        measure_config={"sales": {"fmt": "usd0"}},
    )
    columns = {column["name"]: column for column in table.columns}
    assert columns["sales"]["fmt"] == "usd0"
    assert columns["sales_pct"]["fmt"] == "pct1"
    assert columns["sales_pct"]["viz"] == "delta"
    assert columns["sales_prior"]["title"] == "Prior"


def test_comparison_rejects_bad_period(orders: duckdb.DuckDBPyConnection) -> None:
    with pytest.raises(ValueError):
        comparison_table(
            orders,
            "SELECT * FROM orders",
            dimensions=["category"],
            measures=["sum(sales) AS sales"],
            date_column="order_date",
            compare_vs="fortnightly",
        )
