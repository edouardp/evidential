"""The formatting notebook keeps scientific notation visible and executable."""

import runpy
from pathlib import Path


def test_scientific_formatting_demo_keeps_original_values_and_explicit_formats():
    notebook = Path(__file__).resolve().parents[2] / "notebooks" / "08_column_options.py"
    _, definitions = runpy.run_path(str(notebook))["scientific_formatting"].run()
    table = definitions["scientific"].widget
    assert [row["value"] for row in table.rows] == [123456, 0.000123, -123456, 0, None]
    assert [column.get("fmt") for column in table.columns] == [None, "#,##0.000000", "sci", "0.000E+0"]
