from __future__ import annotations

from collections import Counter

import pytest

from evidential import grouped_records

DATA = [
    {"country": "USA", "city": "NYC", "revenue": 100.0, "orders": 1},
    {"country": "USA", "city": "LA", "revenue": 200.0, "orders": 2},
    {"country": "Canada", "city": "Toronto", "revenue": 80.0, "orders": 3},
]


def test_grouped_records_structure_and_sums() -> None:
    table = grouped_records(DATA, group_by=["country", "city"])
    types = Counter(row["render_type"] for row in table.rows)
    assert types == {"cell_data": 3, "row_subtotal": 2, "row_total": 1}

    total = next(row for row in table.rows if row["render_type"] == "row_total")
    assert total["revenue"] == 380.0
    assert total["orders"] == 6

    usa = next(row for row in table.rows if row["render_type"] == "row_subtotal" and row["country"] == "USA")
    assert usa["revenue"] == 300.0


def test_grouped_records_measures_inferred() -> None:
    table = grouped_records(DATA, group_by="country")
    names = [column["name"] for column in table.columns]
    assert names == ["country", "revenue", "orders"]
    total = next(row for row in table.rows if row["render_type"] == "row_total")
    assert total["revenue"] == 380.0


def test_grouped_records_aggregation() -> None:
    table = grouped_records(
        DATA,
        group_by=["country"],
        measures=["revenue"],
        aggregations={"revenue": "mean"},
    )
    total = next(row for row in table.rows if row["render_type"] == "row_total")
    assert total["revenue"] == pytest.approx((100 + 200 + 80) / 3)


def test_grouped_records_custom_callable() -> None:
    table = grouped_records(
        DATA,
        group_by=["country", "city"],
        measures=["revenue"],
        aggregations={"revenue": max},
        subtotals=False,
    )
    total = next(row for row in table.rows if row["render_type"] == "row_total")
    assert total["revenue"] == 200.0


def test_grouped_records_requires_measures() -> None:
    with pytest.raises(ValueError):
        grouped_records([{"only": "text"}], group_by="only")
