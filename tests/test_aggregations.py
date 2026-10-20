from __future__ import annotations

import statistics

import duckdb
import pytest

from evidential import BUILTIN_AGGREGATIONS, grouped_table, resolve_aggregation
from evidential.aggregations import apply_aggregations, weighted_mean_values
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


def test_builtin_mean_from_detail_values(sales: duckdb.DuckDBPyConnection) -> None:
    table = grouped_table(
        sales,
        "SELECT * FROM sales",
        ["country"],
        ["sum(revenue) AS revenue"],
        aggregations={"revenue": "mean"},
    )
    total = next(row for row in table.display_rows if row["render_type"] == "row_total")
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
    total = next(row for row in table.display_rows if row["render_type"] == "row_total")
    # city-level sums: 100, 250, 80, 120 -> max 250
    assert total["revenue"] == 250.0

    usa = next(row for row in table.display_rows if row["render_type"] == "row_subtotal" and row["country"] == "USA")
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
    total = next(row for row in table.display_rows if row["render_type"] == "row_total")
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
    total = next(row for row in table.display_rows if row["render_type"] == "row_total")
    # aggregated weights for city sums 100, 250, 80, 120 are 1, 3, 1, 1
    expected = (100 * 1 + 250 * 3 + 80 * 1 + 120 * 1) / 6
    assert total["revenue"] == pytest.approx(expected)


def test_unknown_aggregation_raises() -> None:
    with pytest.raises(ValueError):
        resolve_aggregation("bogus")


def test_builtin_registry_has_common_functions() -> None:
    for name in ("sum", "mean", "median", "min", "max", "count", "count_distinct"):
        assert name in BUILTIN_AGGREGATIONS


def test_weighted_mean_keeps_missing_values_and_weights_paired() -> None:
    with duckdb.connect() as connection:
        table = grouped_table(
            connection,
            "SELECT * FROM (VALUES ('A', 1, NULL, 100), ('A', 2, 10, 1), "
            "('A', 3, 20, 1), ('A', 4, 999, NULL)) t(category, item, value, weight)",
            ["category", "item"],
            ["sum(value) AS value"],
            aggregations={"value": "weighted_mean"},
            weight_columns={"value": "weight"},
        )
    summaries = [row for row in table.display_rows if row["render_type"] != "cell_data"]
    assert summaries
    assert all(row["value"] == pytest.approx(15) for row in summaries)


@pytest.mark.parametrize("weights", [[], [1], [1, 1, 1]])
def test_weighted_mean_rejects_mismatched_lengths(weights: list[float]) -> None:
    with pytest.raises(ValueError, match="same length"):
        weighted_mean_values([10, 20], weights)


def test_subtotal_descendant_lookup_scales_with_details_not_group_count() -> None:
    lookups = 0

    class Record(dict):
        def get(self, key, default=None):
            nonlocal lookups
            if key == "__ancestors":
                lookups += 1
            return super().get(key, default)

    details = [Record(value=1, render_type="cell_data", __ancestors=[str(index // 5)]) for index in range(100)]
    summaries = [{"render_type": "row_subtotal", "__group_key": str(index)} for index in range(20)]
    rows = [*details, *summaries, {"render_type": "row_total"}]
    apply_aggregations(rows, {"value": "sum"}, ["value"])
    assert [row["value"] for row in summaries] == [5] * 20
    assert rows[-1]["value"] == 100
    assert lookups <= len(details), f"descendant lookup rescanned details {lookups} times"
