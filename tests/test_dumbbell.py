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


def test_rounded_gradients_are_immutable_and_share_all_declaration_paths():
    palette = ["cyan", "yellow"]
    original = col.range("low", "high", cap="round")
    styled = original.gradient(scale=palette).gradient(min=8, max=26)
    palette.append("red")
    encoding = styled["encodings"][0]
    assert "gradient" not in original["encodings"][0]
    assert encoding["gradient"] == {"color_scale": ["cyan", "yellow"], "min": 8, "max": 26}
    for column in (styled, {"name": "low", "encodings": [encoding]}):
        table = EvidentialTable([{"low": 11, "high": 18}], columns=[column])
        assert table.columns[0]["encodings"][0] == encoding
        table.set_column("low", encodings=[encoding])
        assert table.columns[0]["encodings"][0] == encoding
    composed = col.point("current").range("low", "high", cap="round").gradient(scale="viridis")
    assert "gradient" not in composed["encodings"][0]
    assert composed["encodings"][1]["gradient"] == {"color_scale": "viridis"}


@pytest.mark.parametrize(
    "options",
    [
        {"color_scale": "unknown"},
        {"color_scale": ["red"]},
        {"min": float("nan")},
        {"min": 2, "max": 1},
        {"conditional_colors": "paint"},
        {"color_stops": [{"value": 0, "color": "red"}, {"value": 0, "color": "blue"}]},
    ],
)
def test_range_gradients_validate_mapping_and_update_atomically(options):
    encoding = {"kind": "range", "source": "low", "high": "high", "gradient": options}
    with pytest.raises((ValueError, TypeError)):
        col.range("low", "high", gradient=options)
    table = EvidentialTable([], columns=[col.range("low", "high")])
    original = table.columns
    with pytest.raises((ValueError, TypeError)):
        table.set_column("low", encodings=[encoding])
    assert table.columns == original


def test_gradient_refines_only_ranges_and_rejects_conflicting_colors():
    with pytest.raises(ValueError, match="last range"):
        col.point("x").gradient(scale="viridis")
    for options in ({"color": "red"}, {"color": "@ink"}, {"color_negative": "red"}):
        with pytest.raises(ValueError, match="mutually exclusive"):
            col.range("low", "high", **options).gradient(scale="viridis")
    with pytest.raises(TypeError, match="cap"):
        col.range("low", "high", cap="rounded")
    stops = [{"value": 0, "color": "#00ff0080"}, {"value": 10, "color": "red"}]
    styled = col.range("low", "high").gradient(stops=stops)
    stops[0]["color"] = "blue"
    assert styled["encodings"][0]["gradient"]["color_stops"][0]["color"] == "#00ff0080"


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


def test_weather_notebook_has_twelve_months_and_all_city_choices():
    import runpy
    from pathlib import Path
    from types import SimpleNamespace

    notebook = Path(__file__).resolve().parents[1] / "notebooks" / "61_monthly_weather.py"
    _, definitions = runpy.run_path(str(notebook))["app"].run()
    widget = definitions["monthly_weather"].widget
    assert definitions["city_picker"].value == "New York"
    assert len(definitions["cities"]) == 10
    assert len(widget.rows) == 12
    assert [row["period"] for row in widget.rows][0] == "Jul 2014"
    assert sum(row["days"] for row in widget.rows) == 365
    # Exercise the reactive update cell with another choice, retaining the widget.
    update = runpy.run_path(str(notebook))["update_weather"].run
    columns = widget.columns
    update(
        city_picker=SimpleNamespace(value="Phoenix"),
        monthly_weather=definitions["monthly_weather"],
        weather_rows=definitions["weather_rows"],
    )
    assert widget.columns == columns
    assert {row["city"] for row in widget.rows} == {"Phoenix"}
    assert "Phoenix" in widget.options["title"]
    assert max(row["high"] for row in widget.rows) > 40
    for city in definitions["cities"]:
        months = [row for row in definitions["weather_rows"] if row["city"] == city]
        assert len(months) == 12 and sum(row["days"] for row in months) == 365
        assert all(row["low"] <= row["avg_low"] <= row["avg_high"] <= row["high"] for row in months)


@pytest.mark.parametrize("gradient", ["viridis", 1, ["red", "blue"]])
def test_range_gradient_mapping_requires_a_mapping(gradient):
    with pytest.raises(TypeError, match="color-options mapping"):
        col.range("low", "high", gradient=gradient)


def test_range_gradient_does_not_create_a_misleading_categorical_legend():
    with pytest.raises(ValueError, match="no categorical key"):
        col.range("low", "high").gradient(scale="viridis").legend()
