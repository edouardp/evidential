"""The offline demo runs and exercises actual public column settings."""

import runpy
from pathlib import Path


def test_subcolumn_demo_runs_with_three_examples() -> None:
    notebook = Path(__file__).resolve().parents[2] / "notebooks" / "30_subcolumns.py"
    outputs, definitions = runpy.run_path(str(notebook))["app"].run()
    assert len(outputs) > 3
    observations = definitions["observations"].widget
    assert [column["align"] for column in observations.columns[1:]] == ["right", "left", "center"]
    assert observations.columns[3]["viz"] == "chip"
    economist = definitions["economist"].widget
    assert len(economist.rows) == 43
    assert len(economist.columns) == 10
    assert economist.rows[0]["country"] == "United States"
    assert economist.rows[-1]["country"] == "South Africa"
    assert economist.rows[4]["country"] == "Canada"
    assert economist.rows[9]["gdp_color"] == "#ffc1ae"
    assert economist.rows[33]["cpi_format"] == "num0"
    assert sum(bool(column.get("subcolumn_group")) for column in economist.columns) == 6
    assert any("economist-recreation" in getattr(output, "text", "") for output in outputs)


def test_statistics_demo_includes_ordinary_columns_and_two_and_three_member_groups() -> None:
    notebook = Path(__file__).resolve().parents[2] / "notebooks" / "25_column_stats.py"
    _, definitions = runpy.run_path(str(notebook))["app"].run()
    table = definitions["subcolumn_stats"].widget
    assert table.options["column_stats"] is True
    assert len(table.columns) == 8
    assert sum(column.get("subcolumn_group") == "Activity" for column in table.columns) == 2
    assert sum(column.get("subcolumn_group") == "Fare & payment" for column in table.columns) == 3
    assert sum(not column.get("subcolumn_group") for column in table.columns) == 3
    assert table.columns[3]["fmt"] == "usd2"
    assert table.columns[5]["viz"] == "chip"
