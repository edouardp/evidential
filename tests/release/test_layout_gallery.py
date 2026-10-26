"""The README layout examples execute their real table and row-layout APIs."""

import runpy

import pytest

from evidential import EvidentialTable
from scripts.api_screenshots import LAYOUT_NOTEBOOK, LAYOUTS


@pytest.fixture(scope="module")
def gallery():
    outputs, definitions = runpy.run_path(str(LAYOUT_NOTEBOOK))["app"].run()
    tables = [output for output in outputs if isinstance(output, EvidentialTable)]
    assert len(tables) == len(LAYOUTS)
    return dict(zip((cell for _, cell in LAYOUTS), tables, strict=True)), definitions["layout_data"]


def test_layout_gallery_has_identical_source_records_and_explicit_comparisons(gallery):
    tables, source = gallery
    assert len(source) == 6
    assert all(table.raw == source for table in tables.values())
    assert tables["layout_lines_on"].options["row_lines"] is True
    assert tables["layout_lines_off"].options["row_lines"] is False
    assert [tables[f"layout_shading_{name}"].options["row_shading"] for name in ("off", "one", "three")] == [
        False,
        1,
        3,
    ]
    assert tables["layout_titles"].options["title"] == "Products by region"
    assert tables["layout_titles"].options["subtitle"]
    assert tables["layout_titles"].options["caption"]
    assert tables["layout_footnotes"].columns[0]["footnote"] == "note"


def test_layout_summaries_keep_details_separate_and_do_not_double_count(gallery):
    tables, _ = gallery
    table = tables["layout_combined_totals"]
    plan = table.row_layout
    assert len(table.rows) == 6
    assert len(plan["groups"]) == 2
    assert [group["summary"]["cells"]["sales"]["value"] for group in plan["groups"]] == [3900, 6600]
    assert plan["grand_summary"]["cells"]["sales"]["value"] == 10500
    assert plan["grand_summary"]["cells"]["units"]["value"] == 72
    assert all(group["summary"]["position"] == "top" for group in tables["layout_summary_top"].row_layout["groups"])
    assert all(
        group["summary"]["position"] == "bottom" for group in tables["layout_summary_bottom"].row_layout["groups"]
    )
    assert [group["section"]["label"] for group in tables["layout_heading_values"].row_layout["groups"]] == [
        "North · 3 products",
        "South · 3 products",
    ]


def test_layout_gallery_has_both_header_depths(gallery):
    tables, _ = gallery
    assert tables["layout_groups_one"].columns[1]["column_group"] == "Volume"
    assert tables["layout_groups_two"].columns[1]["column_group"] == ["Operations", "Volume"]


def test_layout_gallery_distinguishes_heading_styles_and_indents_details(gallery):
    tables, _ = gallery
    for name in ("headings", "heading_values", "summary_top", "summary_bottom", "combined_totals"):
        assert tables[f"layout_{name}"].options["section_indent"] == 1
    centered = tables["layout_headings_centered"].row_layout["groups"]
    assert all(group["section"]["align"] == "center" for group in centered)
    column = tables["layout_headings_column"]
    assert column.columns[0]["name"] == "region"
    assert column.columns[0]["repeat_values"] is False
    assert all("section" not in group for group in column.row_layout["groups"])
