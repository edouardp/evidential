"""The error-bar example executes independently and uses meaningful bounds."""

import runpy
from pathlib import Path

import marimo as mo

from evidential import EvidentialTable, col

NOTEBOOK = Path(__file__).resolve().parents[2] / "notebooks/37_encoding_marks.py"


def error_bar_example():
    notebook = runpy.run_path(str(NOTEBOOK))
    _, values = notebook["error_bar_values"].run()
    _, results = notebook["error_bar_example"].run(EvidentialTable=EvidentialTable, col=col, mo=mo, **values)
    return results["error_bar_table"]


def test_error_bar_demo_executes_with_positive_negative_and_cross_zero_intervals():
    table = error_bar_example()
    assert all(row["low"] < row["estimate"] < row["high"] for row in table.rows)
    assert any(row["low"] > 0 for row in table.rows)
    assert any(row["high"] < 0 for row in table.rows)
    assert any(row["low"] < 0 < row["high"] for row in table.rows)
    assert any(abs((row["estimate"] - row["low"]) - (row["high"] - row["estimate"])) > 1e-6 for row in table.rows)
    assert table.columns[1]["scale"]["domain"] == (-11, 4)
    assert [mark["kind"] for mark in table.columns[1]["encodings"]] == ["bar", "range"]
