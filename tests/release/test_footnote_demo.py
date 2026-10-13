"""The footnote demo runs offline and updates a persistent widget."""

import runpy
from pathlib import Path


def test_footnote_demo_exercises_symbol_boundaries_with_a_persistent_widget() -> None:
    notebook = Path(__file__).resolve().parents[2] / "notebooks" / "16_tech_giants.py"
    outputs, definitions = runpy.run_path(str(notebook))["app"].run()
    assert outputs[-1] is None
    table = definitions["footnote_table"].widget
    records = definitions["footnote_records"]
    control = definitions["footnote_count"]
    assert control.value == 12
    assert len(records) == 23
    assert len({row["note"] for row in records}) == 23
    assert len(table.rows) == 12
    assert table.options["footnote_marks"] == "symbols"
    for count in (10, 11, 12, 20, 23):
        table.set_data(records[:count])
        assert len(table.rows) == count
        columns = {column["name"]: column for column in table.columns}
        assert columns["value"]["footnote"] == "note"
        assert columns["value"]["fmt"] == "num1"
        assert columns["note"]["hide"] is True
