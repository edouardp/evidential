"""The centered-bar notebook uses labeled marks and explicit shared scales."""

import runpy
from pathlib import Path


def test_centered_bar_demo_uses_marks_for_every_bar() -> None:
    notebook = Path(__file__).resolve().parents[2] / "notebooks" / "34_centered_bars.py"
    _, definitions = runpy.run_path(str(notebook))["app"].run()
    for name in ("league_table", "variants", "back_to_back", "diverging"):
        table = definitions[name].widget
        bars = [column for column in table.columns if column["type"] == "number"]
        assert bars
        for column in bars:
            assert column.get("viz") != "bar"
            assert column["encodings"][0]["kind"] == "bar"
            if name == "variants" and column["title"] == "Bar only":
                assert not column["encodings"][0].get("label")
            else:
                assert column["encodings"][0]["label"]

    for name in ("league_table", "variants"):
        table = definitions[name].widget
        for column in table.columns[1:]:
            low, high = column["scale"]["domain"]
            assert low == -high
            assert column["references"][0]["value"] == 0
            assert all(abs(row[column["encodings"][0]["source"]]) < high for row in table.rows)

    for name, index, field, expected_format, reference in (
        ("back_to_back", 0, "spend", "usd1", -4.3),
        ("diverging", 1, "tolerance", "pct0", 0),
    ):
        table = definitions[name].widget
        column = table.columns[index]
        encoding = column["encodings"][0]
        assert encoding["label"]["source"] == field
        assert encoding["label"]["format"] == expected_format
        assert column["scale"]["domain"][0] < column["scale"]["domain"][1] == 0
        assert column["references"][0]["value"] == reference
        for row in table.rows:
            assert row[field] > 0
            assert row[encoding["source"]] == -row[field]
