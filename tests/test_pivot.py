from __future__ import annotations

import duckdb
import pytest

from evidential import pivot_table
from evidential.duck import connect


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


@pytest.mark.parametrize(
    ("measure", "expected"),
    [
        ("avg(sales)", 150),
        ("min(sales)", 50),
        ("max(sales)", 250),
        ("count(DISTINCT sales)", 5),
        ("round(avg(sales), 0)", 150),
    ],
)
def test_pivot_totals_aggregate_original_records(sales, measure, expected) -> None:
    table = pivot_table(sales, "SELECT * FROM sales", ["category"], ["year"], [("value", measure)])
    total = next(row for row in table.rows if row["render_type"] == "row_total")
    assert total["value__Total"] == pytest.approx(expected)


def test_pivot_aggregation_overrides_generated_columns(sales) -> None:
    table = pivot_table(
        sales,
        "SELECT * FROM sales",
        ["category"],
        ["year"],
        ["sum(sales) AS sales"],
        aggregations={"sales": "mean"},
    )
    total = next(row for row in table.rows if row["render_type"] == "row_total")
    assert total["sales__2021"] == 150
    assert total["sales__2022"] == 225
    assert total["sales__Total"] == 375
    assert "sales" not in total


def test_pivot_weighted_aggregation(sales) -> None:
    table = pivot_table(
        sales,
        "SELECT *, CASE WHEN category = 'Toys' THEN 1 ELSE 2 END AS weight FROM sales",
        ["category"],
        ["year"],
        ["sum(sales) AS sales"],
        aggregations={"sales": "weighted_mean"},
        weight_columns={"sales": "weight"},
    )
    total = next(row for row in table.rows if row["render_type"] == "row_total")
    assert total["sales__2021"] == pytest.approx((100 + 200 * 2) / 3)
    assert total["sales__2022"] == pytest.approx((150 + 300 * 4) / 5)
    assert all(not key.startswith("__w_") for row in table.rows for key in row)


def test_pivot_total_label_collision_preserves_category_and_total() -> None:
    with duckdb.connect() as connection:
        table = pivot_table(
            connection,
            "SELECT * FROM (VALUES ('A', 'Total', 10), ('A', 'Other', 20)) t(category, p, sales)",
            ["category"],
            ["p"],
            ["sum(sales) AS sales"],
            total=False,
        )
    names = [column["name"] for column in table.columns]
    assert len(names) == len(set(names))
    assert table.rows[0]["sales__Total"] == 30
    assert sorted(table.rows[0][name] for name in names[1:]) == [10, 20, 30]


def test_pivot_labels_with_identical_text_keep_distinct_values() -> None:
    with duckdb.connect() as connection:
        table = pivot_table(
            connection,
            "SELECT * FROM (VALUES ('A', NULL, 10), ('A', '', 20)) t(category, p, sales)",
            ["category"],
            ["p"],
            ["sum(sales) AS sales"],
            total=False,
        )
    names = [column["name"] for column in table.columns]
    assert len(names) == len(set(names))
    assert sorted(table.rows[0][name] for name in names[1:]) == [10, 20, 30]


def test_pivot_distinct_count_deduplicates_across_groups() -> None:
    with duckdb.connect() as connection:
        table = pivot_table(
            connection,
            "SELECT * FROM (VALUES ('A', 2021, 10), ('B', 2022, 10)) t(category, year, sales)",
            ["category"],
            ["year"],
            ["count(DISTINCT sales) AS sales"],
        )
    total = next(row for row in table.rows if row["render_type"] == "row_total")
    assert total["sales__Total"] == 1


def test_pivot_subtotals_use_raw_values_without_total_column() -> None:
    with duckdb.connect() as connection:
        table = pivot_table(
            connection,
            "SELECT * FROM (VALUES ('A', 'X', 2021, 10), ('A', 'Y', 2021, 30), "
            "('A', 'Y', 2021, 50)) t(category, item, year, sales)",
            ["category", "item"],
            ["year"],
            ["avg(sales) AS sales"],
            show_total_column=False,
        )
    summaries = [row for row in table.rows if row["render_type"] != "cell_data"]
    assert len(summaries) == 2
    assert all(row["sales__2021"] == 30 for row in summaries)
