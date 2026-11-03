"""Sparkline gradients reuse the fluent cell-color API and mapping declaration."""

import math

import pytest

from evidential import EvidentialTable, col, domain


@pytest.mark.parametrize("style", ["line", "area", "bar", "points", "change"])
def test_fluent_factory_and_mapping_gradients_share_one_color_declaration(style):
    colors = {"color_scale": ["red", "gray", "blue"], "min": -4, "max": 9, "midpoint": 0}
    columns = [
        col.sparkline("series", type=style).color(scale=["red", "gray", "blue"], min=-4, max=9, midpoint=0),
        col.array("series").color(scale=["red", "gray", "blue"], min=-4, max=9, midpoint=0).sparkline(type=style),
        {
            "name": "series",
            "type": "array",
            "viz": "sparkline",
            "sparkline_options": {"type": style},
            "color_options": colors,
        },
    ]
    for column in columns:
        spec = EvidentialTable([{"series": [-3, 0, 8]}], columns=[column]).columns[0]
        assert spec["viz"] == "sparkline"
        assert spec["sparkline_options"] == {"type": style}
        assert spec["color_options"] == colors


def test_gradient_refinement_copies_palettes_and_stops_without_mutating_base():
    base = col.sparkline("series", type="area")
    palette = ["red", "blue"]
    refined = base.color(scale=palette).color(min=-5, max=5)
    palette[0] = "green"
    assert "color_options" not in base
    assert refined["color_options"] == {"color_scale": ["red", "blue"], "min": -5, "max": 5}
    stops = [{"value": -5, "color": "red"}, {"value": 5, "color": "blue"}]
    explicit = base.color(stops=stops)
    stops[0]["color"] = "green"
    assert explicit["color_options"]["color_stops"][0]["color"] == "red"
    assert base.color()["viz"] == "sparkline"


@pytest.mark.parametrize("style", ["line", "area", "bar", "points", "change"])
def test_legacy_gradient_keywords_remain_available_for_all_styles(style):
    column = col.sparkline("series", type=style, color_scale="viridis", color_domain=(-4, 9))
    assert column["sparkline_options"]["color_scale"] == "viridis"
    assert EvidentialTable([{"series": [1]}], columns=[column]).columns[0]["viz"] == "sparkline"


@pytest.mark.parametrize(
    "colors",
    [
        {"color_scale": "unknown"},
        {"color_scale": ["red"]},
        {"color_scale": ["red", ""]},
        {"min": math.nan},
        {"max": math.inf},
        {"midpoint": math.inf},
        {"min": 2, "max": 1},
        {"min": 1, "max": 1},
        {"conditional_colors": "paint"},
        {"scale_column": "other"},
        {"color_stops": [{"value": 0, "color": "red"}]},
        {"color_stops": [{"value": 0, "color": "red"}, {"value": 0, "color": "blue"}]},
        {"color_stops": [{"value": 0, "color": "red"}, {"value": math.inf, "color": "blue"}]},
    ],
)
def test_invalid_gradients_fail_on_builder_and_mapping_paths(colors):
    arguments = {
        "scale" if key == "color_scale" else "stops" if key == "color_stops" else key: value
        for key, value in colors.items()
    }
    with pytest.raises((ValueError, TypeError)):
        col.sparkline("series").color(**arguments)
    with pytest.raises((ValueError, TypeError)):
        EvidentialTable(
            [{"series": [1]}],
            columns=[
                {
                    "name": "series",
                    "viz": "sparkline",
                    "color_options": colors,
                }
            ],
        )


def test_ambiguous_colors_and_change_neutral_conflicts_are_rejected():
    with pytest.raises(ValueError, match="mutually exclusive"):
        col.sparkline("series", color="red").color(scale="viridis")
    with pytest.raises(ValueError, match="Conflicting.*scales"):
        col.sparkline("series", color_scale="viridis").color(scale="magma")
    with pytest.raises(ValueError, match="Conflicting.*bounds"):
        col.sparkline("series", color_scale="viridis", color_domain=(-2, 2)).color(min=-3)
    with pytest.raises(ValueError, match="steady"):
        col.sparkline("series", type="change", steady=(-1, 1)).color(scale="RdBu", min=0)
    with pytest.raises(ValueError, match="midpoint.*steady"):
        col.sparkline("series", type="change").color(scale="RdBu", midpoint=1)


def test_shared_domains_support_the_same_palette_for_sparkline_and_scalar_cells():
    shared = domain.numeric("temperature").bounds(-10, 30).palette("RdBu").midpoint(0)
    table = EvidentialTable(
        [{"series": [-5, 0, 20], "value": 0}],
        columns=[
            col.sparkline("series", type="line").domain(shared),
            col.number("value").color(scale="RdBu").domain(shared),
        ],
    )
    assert table.columns[0]["domain"] == table.columns[1]["domain"]
    with pytest.raises(ValueError, match="constant sparkline"):
        EvidentialTable([{"series": [1]}], columns=[col.sparkline("series", color="red").domain(shared)])
