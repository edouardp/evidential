"""Adjacent differences are an opt-in input mode for change sparklines."""

import runpy
from pathlib import Path

import pytest

from evidential import EvidentialTable, col


def test_delta_is_shared_by_factory_fluent_mapping_and_table_updates():
    source = [{"values": [3, 5, 4, 7, 9, 8]}]
    options = {"type": "change", "delta": True, "steady": (-0.5, 0.5)}
    for column in (
        col.sparkline("values", **options),
        col.array("values").sparkline(**options),
        {"name": "values", "viz": "sparkline", "sparkline_options": options},
    ):
        table = EvidentialTable(source, columns=[column])
        assert table.columns[0]["sparkline_options"] == options
        assert table.rows[0]["values"] == source[0]["values"]
        table.set_column("values", sparkline_options={"type": "change", "delta": False})
        assert table.columns[0]["sparkline_options"]["delta"] is False
    refined = col.sparkline("values", type="change", delta=True).sparkline(delta=False)
    assert refined["sparkline_options"]["delta"] is False
    assert "delta" not in col.sparkline("values", type="change")["sparkline_options"]


@pytest.mark.parametrize("style", ["line", "area", "bar", "points"])
def test_delta_is_only_valid_for_change_sparklines(style):
    with pytest.raises(ValueError, match="type='change'"):
        col.sparkline("values", type=style, delta=True)
    with pytest.raises(ValueError, match="type='change'"):
        EvidentialTable(
            [], columns=[{"name": "values", "viz": "sparkline", "sparkline_options": {"type": style, "delta": True}}]
        )


@pytest.mark.parametrize("value", [0, 1, "true", [], {}])
def test_delta_requires_a_boolean_and_invalid_updates_are_atomic(value):
    with pytest.raises(TypeError, match="delta"):
        col.sparkline("values", type="change", delta=value)
    table = EvidentialTable([], columns=[col.sparkline("values", type="change")])
    original = table.columns
    with pytest.raises(TypeError, match="delta"):
        table.set_column("values", sparkline_options={"type": "change", "delta": value})
    assert table.columns == original


def test_five_style_notebook_uses_delta_for_absolute_measurements():
    notebook = Path(__file__).resolve().parents[1] / "notebooks" / "40_sparklines_and_booleans.py"
    outputs, _ = runpy.run_path(str(notebook))["app"].run()
    styles = next(
        output.widget
        for output in outputs
        if hasattr(output, "widget") and output.widget.options["title"] == "One series, five styles"
    )
    assert styles.columns[-1]["sparkline_options"] == {"type": "change", "delta": True}
    assert styles.rows[0]["values"] == [3, 5, 4, 7, 9, 8, 11, 13]
