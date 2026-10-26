"""The screenshot notebook stays a working, representative API example."""

from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / "notebooks" / "49_api_screenshots.py"


def _preview():
    return runpy.run_path(str(NOTEBOOK))["app"].run()[1]["preview_table"]


def test_preview_revenue_label_falls_back_inside_the_bar():
    """A bar too full for an outside label must move its annotation inside."""
    preview = _preview()
    revenue = next(column for column in preview.columns if column["name"] == "revenue")
    assert revenue["encodings"][0]["label"] == {"value": True, "position": "outside_end", "auto": True}
    assert any(row["city"] == "London" for row in preview.rows)


def test_preview_shows_sections_subcolumns_and_two_footnotes():
    preview = _preview()
    sections = [row["__label"] for row in preview.display_rows if row.get("render_type") == "row_section"]
    assert sections == ["Americas", "Europe", "Asia-Pacific"]

    by_name = {column["name"]: column for column in preview.columns}
    assert by_name["revenue"]["subcolumn_group"] == "Revenue (US$m) · latest / prior"
    assert by_name["revenue_prior"]["subcolumn_group"] == "Revenue (US$m) · latest / prior"

    assert by_name["revenue_prior"]["footnote"] == "revenue_note"
    assert by_name["occupancy"]["footnote"] == "occupancy_note"
    assert sum(row.get("revenue_note") is not None for row in preview.rows) == 1
    assert sum(row.get("occupancy_note") is not None for row in preview.rows) == 1
