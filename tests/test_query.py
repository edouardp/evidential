from __future__ import annotations

import duckdb
import pytest

from evidential import date_range_sql, query_table
from evidential.duck import connect


@pytest.fixture()
def orders() -> duckdb.DuckDBPyConnection:
    connection = connect()
    connection.execute(
        """
        CREATE TABLE orders AS SELECT * FROM (VALUES
            ('A', DATE '2023-01-15', 10.0),
            ('B', DATE '2024-06-01', 20.0),
            ('C', DATE '2024-06-15', 30.0)
        ) AS v(customer, order_date, sales)
        """
    )
    return connection


def test_query_table_where_order_limit(orders: duckdb.DuckDBPyConnection) -> None:
    table = query_table(
        orders,
        "SELECT * FROM orders",
        where="sales >= 20",
        order="sales DESC",
        limit=1,
    )
    assert [row["customer"] for row in table.rows] == ["C"]


def test_query_table_date_range_mapping(orders: duckdb.DuckDBPyConnection) -> None:
    table = query_table(
        orders,
        "SELECT * FROM orders",
        date_range={"range": "2024-06-01 to 2024-07-01", "date": "order_date"},
    )
    assert sorted(row["customer"] for row in table.rows) == ["B", "C"]


def test_date_range_presets(orders: duckdb.DuckDBPyConnection) -> None:
    assert date_range_sql("all time", "d") is None
    assert "AND d <" in date_range_sql("2020-01-01 to 2020-02-01", "d")
    assert date_range_sql("from 2020-01-01", "d").startswith("d >=")
    assert date_range_sql("until 2020-01-01", "d").startswith("d <")
    assert "INTERVAL '90 day'" in date_range_sql("Last 90 days", "d")
    assert "date_trunc('month'" in date_range_sql("previous month", "d")
    assert "date_trunc('year'" in date_range_sql("year to date", "d")
    assert date_range_sql("today", "d")
    with pytest.raises(ValueError):
        date_range_sql("nonsense", "d")


def test_page_size_all_is_documented() -> None:
    # `page_size="all"` is handled by the renderer; Python just passes it through.
    from evidential import EvidentialTable

    table = EvidentialTable([{"a": 1}], page_size="all")
    assert table.options["page_size"] == "all"


@pytest.mark.parametrize("spec", ["from 2020-01-01'OR'1'='1", "until 2024-99-01", "2024-01-01 to bad"])
def test_custom_ranges_reject_invalid_dates(spec) -> None:
    with pytest.raises(ValueError, match="date"):
        date_range_sql(spec, "d")


@pytest.mark.parametrize("spec", ["month to date", "year to date", "week to date", "quarter to date"])
def test_to_date_includes_todays_timestamps(spec) -> None:
    with duckdb.connect() as connection:
        condition = date_range_sql(spec, "d")
        assert connection.sql(
            f"SELECT {condition} FROM (SELECT CURRENT_DATE + INTERVAL '12 hours' AS d)"
        ).fetchone() == (True,)


@pytest.mark.parametrize("spec", ["until 2024-01-01", "2023-12-01 to 2024-01-01"])
def test_explicit_date_end_includes_entire_day(spec) -> None:
    with duckdb.connect() as connection:
        table = query_table(
            connection,
            "SELECT * FROM (VALUES (TIMESTAMP '2024-01-01 12:00:00'), (TIMESTAMP '2024-01-02 00:00:00')) t(d)",
            date_range=spec,
            date_column="d",
        )
    assert [row["d"] for row in table.rows] == ["2024-01-01T12:00:00"]
