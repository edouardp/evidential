"""The screenshot notebook stays a working, representative API example."""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / "notebooks" / "49_api_screenshots.py"


def _table(name):
    return runpy.run_path(str(NOTEBOOK))["app"].run()[1][name]


def test_preview_revenue_label_falls_back_inside_the_bar():
    """A bar too full for an outside label must move its annotation inside."""
    preview = _table("preview_table")
    revenue = next(column for column in preview.columns if column["name"] == "revenue")
    assert revenue["encodings"][0]["label"] == {"value": True, "position": "outside_end", "auto": True}
    assert any(row["city"] == "London" for row in preview.rows)


def test_preview_shows_sections_subcolumns_and_two_footnotes():
    preview = _table("preview_table")
    sections = [row["__label"] for row in preview.display_rows if row.get("render_type") == "row_section"]
    assert sections == ["Americas", "Europe", "Asia-Pacific"]

    by_name = {column["name"]: column for column in preview.columns}
    assert by_name["revenue"]["subcolumn_group"] == "Revenue (US$m) · latest / prior"
    assert by_name["revenue_prior"]["subcolumn_group"] == "Revenue (US$m) · latest / prior"

    assert by_name["revenue_prior"]["footnote"] == "revenue_note"
    assert by_name["occupancy"]["footnote"] == "occupancy_note"
    assert sum(row.get("revenue_note") is not None for row in preview.rows) == 1
    assert sum(row.get("occupancy_note") is not None for row in preview.rows) == 1


def test_sales_by_year_shows_explicit_year_columns_and_an_overall_total():
    table = _table("sales_by_year_table")
    fields = ["category", "sales_2019", "sales_2020", "sales_2021", "total"]
    assert [column["name"] for column in table.columns] == fields
    *categories, overall = table.raw
    assert categories
    assert overall["category"] == "Total"
    for field in fields[1:]:
        assert overall[field] == pytest.approx(sum(row[field] for row in categories))


def test_grouped_totals_example_places_subtotals_in_the_row_layout():
    table = _table("grouped_totals_table")
    assert len(table.raw) == 12
    for group in table.row_layout["groups"]:
        assert group["section"]["collapsed_summary"] is True
        subtotal = group["summary"]
        assert subtotal["position"] == "top"
        assert subtotal["cells"]["orders"]["value"] == sum(table.raw[index]["orders"] for index in group["members"])
    assert table.row_layout["grand_summary"]["cells"]["orders"]["value"] == 10_000
