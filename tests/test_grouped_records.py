"""Exercise grouped display metadata through the public in-memory API."""

from __future__ import annotations

import statistics
from collections import Counter

import pytest

from evidential import grouped_records

# Each row is already at the city level, like the old SQL builder's detail rows.
SALES = [
    {"country": "USA", "city": "NYC", "revenue": 100.0, "orders": 1},
    {"country": "USA", "city": "LA", "revenue": 250.0, "orders": 2},
    {"country": "Canada", "city": "Toronto", "revenue": 80.0, "orders": 1},
    {"country": "Canada", "city": "Vancouver", "revenue": 120.0, "orders": 1},
]


def test_grouped_rows_have_render_metadata() -> None:
    table = grouped_records(rows=SALES, group_by=["country", "city"], measures=["revenue"])
    display = table.display_rows
    assert Counter(row["render_type"] for row in display) == {"cell_data": 4, "row_subtotal": 2, "row_total": 1}

    subtotals = {row["country"]: row for row in display if row["render_type"] == "row_subtotal"}
    for subtotal in subtotals.values():
        assert subtotal["__level"] == 1
        assert subtotal["__ancestors"] == []
        assert subtotal["__parent_key"] is None
        assert subtotal["city"] == ""

    for detail in table.rows:
        key = subtotals[detail["country"]]["__group_key"]
        assert detail["__level"] == 2
        assert detail["__ancestors"] == [key]
        assert detail["__parent_key"] == key

    total = display[-1]
    assert total["render_type"] == "row_total"
    assert total["__level"] == 0
    assert total["__ancestors"] == []
    assert total["__parent_key"] is None
    assert total["city"] == ""


@pytest.mark.parametrize("total_label", ["Total", "All countries"])
def test_grand_total_label_and_value(total_label: str) -> None:
    table = grouped_records(rows=SALES, group_by=["country", "city"], total_label=total_label)
    total = next(row for row in table.display_rows if row["render_type"] == "row_total")
    assert total["country"] == total_label
    assert total["revenue"] == 550.0
    assert total["orders"] == 5
    assert table.options["show_total_row"] is True


@pytest.mark.parametrize("total", [False, True])
def test_subtotals_can_be_disabled_independently_of_the_grand_total(total: bool) -> None:
    table = grouped_records(rows=SALES, group_by=["country", "city"], subtotals=False, total=total)
    expected = Counter({"cell_data": len(SALES)})
    if total:
        expected["row_total"] = 1
    assert Counter(row["render_type"] for row in table.display_rows) == expected
    assert table.options["show_total_row"] is total


@pytest.mark.parametrize("subtotal_position", ["top", "bottom"])
@pytest.mark.parametrize("total_position", ["top", "bottom"])
def test_subtotal_and_total_positions(subtotal_position: str, total_position: str) -> None:
    table = grouped_records(
        rows=SALES,
        group_by=["country", "city"],
        subtotal_position=subtotal_position,
        total_position=total_position,
    )
    display = table.display_rows
    total_index = 0 if total_position == "top" else len(display) - 1
    assert display[total_index]["render_type"] == "row_total"

    for country in ("Canada", "USA"):
        types = [row["render_type"] for row in display if row["country"] == country]
        if subtotal_position == "top":
            assert types == ["row_subtotal", "cell_data", "cell_data"]
        else:
            assert types == ["cell_data", "cell_data", "row_subtotal"]


def test_named_measures_and_column_configuration() -> None:
    table = grouped_records(
        rows=SALES,
        group_by=["country", "city"],
        measures=["orders", "revenue"],
        dimension_config={"country": {"title": "Country"}},
        measure_config={"revenue": {"fmt": "usd0", "viz": "bar"}},
    )
    columns = {column["name"]: column for column in table.columns}
    assert list(columns) == ["country", "city", "orders", "revenue"]
    assert columns["country"]["title"] == "Country"
    assert columns["revenue"]["fmt"] == "usd0"
    assert columns["revenue"]["viz"] == "bar"
    assert columns["revenue"]["align"] == "right"


def test_nested_groups_keep_blank_and_missing_values_distinct() -> None:
    table = grouped_records(
        rows=[
            {"country": "USA", "city": None, "channel": "Shop", "sales": 10},
            {"country": "USA", "city": "", "channel": "Shop", "sales": 20},
        ],
        group_by=["country", "city", "channel"],
    )
    levels = [row for row in table.display_rows if row["render_type"] == "row_subtotal"]
    country = next(row for row in levels if row["__level"] == 1)
    cities = {row["city"]: row for row in levels if row["__level"] == 2}
    assert set(cities) == {None, ""}
    assert cities[None]["__group_key"] != cities[""]["__group_key"]
    for detail in table.rows:
        subtotal = cities[detail["city"]]
        assert subtotal["sales"] == detail["sales"]
        assert subtotal["channel"] == ""
        assert subtotal["__ancestors"] == [country["__group_key"]]
        assert subtotal["__parent_key"] == country["__group_key"]
        assert detail["__ancestors"] == [country["__group_key"], subtotal["__group_key"]]
        assert detail["__parent_key"] == subtotal["__group_key"]


@pytest.mark.parametrize(
    ("aggregation", "subtotal_expected", "total_expected"),
    [
        ("mean", 30, 25),
        ("min", 10, 10),
        ("max", 50, 50),
        ("count_distinct", 3, 3),
        (lambda values: round(statistics.fmean(values)), 30, 25),
    ],
)
def test_nonadditive_summaries_use_all_original_records(aggregation, subtotal_expected, total_expected) -> None:
    table = grouped_records(
        rows=[
            {"category": "A", "item": "X", "sales": 10},
            {"category": "A", "item": "Y", "sales": 30},
            {"category": "A", "item": "Y", "sales": 50},
            {"category": "B", "item": "Z", "sales": 10},
        ],
        group_by=["category", "item"],
        aggregations={"sales": aggregation},
    )
    subtotal = next(
        row for row in table.display_rows if row["render_type"] == "row_subtotal" and row["category"] == "A"
    )
    total = next(row for row in table.display_rows if row["render_type"] == "row_total")
    assert subtotal["sales"] == pytest.approx(subtotal_expected)
    assert total["sales"] == pytest.approx(total_expected)
