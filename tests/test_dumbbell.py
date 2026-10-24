"""Ordered range endpoints support signed color and direction annotations."""

import pytest

from evidential import EvidentialTable, col


def test_directional_ranges_share_factory_fluent_mapping_and_update_validation():
    encoding = {
        "kind": "range",
        "source": "before",
        "high": "after",
        "color": "black",
        "color_negative": "red",
        "direction_marker": True,
    }
    rows = [{"before": 10, "after": 8}]
    for column in (
        col.range("before", "after", color="black", color_negative="red", direction_marker=True),
        col.point("before").range("before", "after", color="black", color_negative="red", direction_marker=True),
        {"name": "before", "encodings": [encoding]},
    ):
        table = EvidentialTable(rows, columns=[column])
        assert table.columns[0]["encodings"][-1] == encoding
        assert table.rows[0]["before"] == 10 and table.rows[0]["after"] == 8
    table.set_column("before", encodings=[{**encoding, "direction_marker": False}])
    assert table.columns[0]["encodings"][0]["direction_marker"] is False


def test_range_negative_colors_accept_column_and_callable_bindings():
    rows = [{"before": 10, "after": 8, "ink": "red"}]
    referenced = EvidentialTable(rows, columns=[col.range("before", "after", color_negative="@ink")])
    assert referenced.columns[0]["encodings"][0]["color_negative_column"] == "ink"
    computed = EvidentialTable(rows, columns=[col.range("before", "after", color_negative=lambda row: row["ink"])])
    field = computed.columns[0]["encodings"][0]["color_negative_column"]
    assert computed.rows[0][field] == "red"


@pytest.mark.parametrize("value", [1, "true", [], {}])
def test_direction_marker_requires_a_boolean_on_all_paths(value):
    encoding = {"kind": "range", "source": "before", "high": "after", "direction_marker": value}
    with pytest.raises(TypeError, match="direction_marker"):
        col.range("before", "after", direction_marker=value)
    with pytest.raises(TypeError, match="direction_marker"):
        EvidentialTable([], columns=[{"name": "before", "encodings": [encoding]}])
    table = EvidentialTable([], columns=[col.range("before", "after")])
    original = table.columns
    with pytest.raises(TypeError, match="direction_marker"):
        table.set_column("before", encodings=[encoding])
    assert table.columns == original


@pytest.mark.parametrize("kind", ["bar", "point", "points", "stacked_bar"])
def test_direction_markers_are_range_only(kind):
    with pytest.raises(ValueError, match="direction_marker"):
        EvidentialTable(
            [], columns=[{"name": "x", "encodings": [{"kind": kind, "source": "x", "direction_marker": True}]}]
        )


def test_existing_ranges_keep_their_wire_defaults():
    assert col.range("before", "after")["encodings"] == [{"kind": "range", "source": "before", "high": "after"}]


def test_dumbbell_notebook_runs_and_compares_optional_features():
    import runpy
    from pathlib import Path

    notebook = Path(__file__).resolve().parents[1] / "notebooks" / "48_dumbbell_plots.py"
    _, definitions = runpy.run_path(str(notebook))["app"].run()
    for name in ("plain", "negative", "directed"):
        assert len(definitions[name].widget.rows) == 5
    assert len(definitions["signed"].widget.rows) == 4
    plain = definitions["plain"].widget.columns[1]["encodings"][0]
    negative = definitions["negative"].widget.columns[1]["encodings"][0]
    directed = definitions["directed"].widget.columns[1]["encodings"][0]
    assert "color_negative" not in plain and "direction_marker" not in plain
    assert negative["color_negative"] == "#cc1111" and "direction_marker" not in negative
    assert directed["color_negative"] == "#cc1111" and directed["direction_marker"] is True
