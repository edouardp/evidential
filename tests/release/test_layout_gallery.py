"""The README layout examples execute their real table and row-layout APIs."""

import ast
import runpy

import pytest

from evidential import EvidentialTable
from scripts.api_screenshots import LAYOUT_NOTEBOOK, LAYOUTS
from scripts.generate_readme import example_code


@pytest.fixture(scope="module")
def gallery():
    outputs, definitions = runpy.run_path(str(LAYOUT_NOTEBOOK))["app"].run()
    tables = [output for output in outputs if isinstance(output, EvidentialTable)]
    assert len(tables) == len(LAYOUTS)
    connection = definitions["con"]
    source = connection.sql("SELECT * FROM orders")
    records = [dict(zip(source.columns, row, strict=True)) for row in source.fetchall()]
    try:
        yield dict(zip((cell for _, cell in LAYOUTS), tables, strict=True)), records
    finally:
        connection.close()


def test_layout_gallery_has_identical_source_records_and_explicit_comparisons(gallery):
    tables, source = gallery
    assert len(source) == 6
    for table in tables.values():
        fields = table.raw[0].keys()
        assert table.raw == [{field: record[field] for field in fields} for record in source]
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


def test_layout_excerpts_show_real_queries_and_required_source_fields(gallery):
    tables, _ = gallery
    source = LAYOUT_NOTEBOOK.read_text()
    for name, table in tables.items():
        excerpt = example_code(source, name, mode="call")
        call = ast.parse(excerpt, mode="eval").body
        assert isinstance(call, ast.Call)
        columns = next(arg.value for arg in call.keywords if arg.arg == "columns")
        if isinstance(columns, ast.List):
            assert not any(isinstance(item, ast.Starred) for item in columns.elts)
        query = call.args[0]
        assert isinstance(query, ast.Call)
        assert ast.unparse(query.func) == "con.sql"
        assert isinstance(query.args[0], ast.Constant)
        sql = query.args[0].value
        assert sql.startswith("SELECT ") and sql.endswith(" FROM orders")
        assert "*" not in sql
        fields = sql.removeprefix("SELECT ").removesuffix(" FROM orders").split(", ")
        assert fields == list(table.raw[0])
        assert set(fields) >= {column["name"] for column in table.columns}
        if table.row_layout.get("groups"):
            assert "region" in fields
        if name == "layout_footnotes":
            assert "note" in fields


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
    assert column.columns[0]["font_weight"] == "600"
    assert all("section" not in group for group in column.row_layout["groups"])
