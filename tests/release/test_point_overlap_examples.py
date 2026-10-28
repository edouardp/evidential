"""The dumbbell gallery prints its overlap cases and keeps translucent controls."""

import runpy
from pathlib import Path


def test_dumbbell_notebook_exposes_two_three_four_and_nearly_equal_cases():
    notebook = Path(__file__).resolve().parents[2] / "notebooks/48_dumbbell_plots.py"
    _, definitions = runpy.run_path(str(notebook))["app"].run()
    table = definitions["overlap_table"].widget
    assert len(table.raw) == 7
    assert [col["name"] for col in table.columns[:5]] == ["case", "before", "after", "target", "forecast"]
    fields = ["before", "after", "target", "forecast"]
    assert [sum(row[field] is not None for field in fields) for row in table.raw[:3]] == [2, 3, 4]
    assert len({table.raw[3][field] for field in fields}) == 4
    transparent = definitions["transparent_table"].widget
    assert all(color.endswith("80") for color in transparent.columns[-1]["encodings"][0]["palette"])
