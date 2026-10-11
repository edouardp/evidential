from __future__ import annotations

import statistics

import duckdb
import pytest

from evidence_tables import BUILTIN_AGGREGATIONS, grouped_table, resolve_aggregation
from evidence_tables.duck import connect


@pytest.fixture()
def sales() -> duckdb.DuckDBPyConnection:
    connection = connect()
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


def test_builtin_mean_from_detail_values(sales: duckdb.DuckDBPyConnection) -> None:
    table = grouped_table(
        sales,
        "SELECT * FROM sales",
        ["country"],
        ["sum(revenue) AS revenue"],
        aggregations={"revenue": "mean"},
    )
    total = next(row for row in table.rows if row["render_type"] == "row_total")
    # country-level sums are USA=350 and Canada=200 -> mean 275
    assert total["revenue"] == pytest.approx(275.0)


def test_custom_callable_aggregation(sales: duckdb.DuckDBPyConnection) -> None:
    table = grouped_table(
        sales,
        "SELECT * FROM sales",
        ["country", "city"],
        ["sum(revenue) AS revenue"],
        aggregations={"revenue": max},
    )
    total = next(row for row in table.rows if row["render_type"] == "row_total")
    # city-level sums: 100, 250, 80, 120 -> max 250
    assert total["revenue"] == 250.0

    usa = next(
        row for row in table.rows if row["render_type"] == "row_subtotal" and row["country"] == "USA"
    )
    assert usa["revenue"] == 250.0  # max of NYC 100, LA 250


def test_aggregation_applies_to_all_measures(sales: duckdb.DuckDBPyConnection) -> None:
    table = grouped_table(
        sales,
        "SELECT * FROM sales",
        ["country", "city"],
        ["sum(revenue) AS revenue", "count(*) AS orders"],
        aggregations=statistics.median,
        subtotals=False,
    )
    total = next(row for row in table.rows if row["render_type"] == "row_total")
    assert total["revenue"] == pytest.approx(110.0)  # median of 100/250/80/120
    assert total["orders"] == 1  # median of four 1s


def test_weighted_mean(sales: duckdb.DuckDBPyConnection) -> None:
    sales.execute("ALTER TABLE sales ADD COLUMN weight DOUBLE")
    sales.execute(
        """
        UPDATE sales SET weight = CASE
            WHEN city = 'NYC' THEN 1
            WHEN city = 'LA' THEN 1.5
            WHEN city = 'Toronto' THEN 1
            WHEN city = 'Vancouver' THEN 1
            ELSE 1 END
        """
    )
    table = grouped_table(
        sales,
        "SELECT * FROM sales",
        ["country", "city"],
        ["sum(revenue) AS revenue"],
        aggregations={"revenue": "weighted_mean"},
        weight_columns={"revenue": "weight"},
    )
    total = next(row for row in table.rows if row["render_type"] == "row_total")
    # aggregated weights for city sums 100, 250, 80, 120 are 1, 3, 1, 1
    expected = (100 * 1 + 250 * 3 + 80 * 1 + 120 * 1) / 6
    assert total["revenue"] == pytest.approx(expected)


def test_unknown_aggregation_raises() -> None:
    with pytest.raises(ValueError):
        resolve_aggregation("bogus")


def test_builtin_registry_has_common_functions() -> None:
    for name in ("sum", "mean", "median", "min", "max", "count", "count_distinct"):
        assert name in BUILTIN_AGGREGATIONS
