"""A common gradient declaration across numeric visualizations and their scale keys."""

import pytest

from evidential import EvidentialTable, col


def columns():
    return [
        col.bar("x"),
        col.point("x"),
        col.points("samples"),
        col.points(["x", "y"]),
        col.range("x", "y"),
        col.boxplot("minimum", "q1", "median", "q3", "maximum"),
        col.distribution("density"),
    ]


def test_all_numeric_marks_share_immutable_gradient_options_and_mapping_updates():
    palette = ["red", "white", "blue"]
    for original in columns():
        styled = original.gradient(scale=palette, min=-10, max=10, midpoint=0).scale(gradient=True)
        encoding = styled["encodings"][-1]
        assert encoding["gradient"] == {"color_scale": palette, "min": -10, "max": 10, "midpoint": 0}
        assert "gradient" not in original["encodings"][-1]
        assert styled["scale"]["axis"] is True
        table = EvidentialTable([], columns=[styled])
        assert table.columns[0]["encodings"][-1] == encoding
        table.set_column(styled["name"], encodings=[encoding], scale={"gradient": True})
        assert table.columns[0]["scale"]["axis"] is True
    palette.append("black")
    assert len(styled["encodings"][-1]["gradient"]["color_scale"]) == 3


def test_cells_and_sparklines_share_the_existing_color_configuration():
    for original in [col.number("x"), col.sparkline("samples", type="area"), col.sparkline("samples", type="points")]:
        args = {"scale": ["red", "white", "blue"], "min": -10, "max": 10, "midpoint": 0}
        assert dict(original.gradient(**args)) == dict(original.color(**args))
    with pytest.raises(ValueError, match="numeric cell"):
        col.rating("x").gradient(scale="viridis")


@pytest.mark.parametrize(
    "options",
    [
        {"color_scale": "unknown"},
        {"min": 2, "max": 1},
        {"max": float("nan")},
        {"conditional_colors": "color"},
        {"color_stops": [{"value": 0, "color": "red"}, {"value": 0, "color": "blue"}]},
    ],
)
def test_invalid_gradients_fail_for_every_mark_and_atomic_updates(options):
    for original in columns():
        enc = {**original["encodings"][-1], "gradient": options}
        with pytest.raises((TypeError, ValueError)):
            EvidentialTable([], columns=[{"name": "x", "encodings": [enc]}])
        table = EvidentialTable([], columns=[original])
        before = table.columns
        with pytest.raises((TypeError, ValueError)):
            table.set_column(original["name"], encodings=[enc])
        assert table.columns == before


def test_color_key_requires_a_gradient_and_a_visible_axis_and_has_bool_validation():
    for options in ({"axis": False, "gradient": True}, {"axis": "yes", "gradient": True}, {"gradient": "viridis"}):
        with pytest.raises((TypeError, ValueError)):
            col.bar("x").gradient(scale="viridis").scale(**options)
        with pytest.raises((TypeError, ValueError)):
            EvidentialTable(
                [],
                columns=[
                    {"name": "x", "encodings": col.bar("x").gradient(scale="viridis")["encodings"], "scale": options}
                ],
            )
    with pytest.raises(ValueError, match="needs a numeric mark gradient"):
        EvidentialTable([], columns=[col.bar("x").scale(gradient=True)])
    with pytest.raises(ValueError, match="needs a numeric mark gradient"):
        EvidentialTable([], columns=[{"name": "x", "scale": {"gradient": True}}])
    # Builders can declare the scale before the mark gradient; full-table
    # validation checks the final composition, not the intermediate builder.
    assert EvidentialTable([], columns=[col.bar("x").scale(gradient=True).gradient(scale="viridis")]).columns
    valid = col.bar("x").gradient(scale="viridis").scale(gradient=True).scale(gradient=False, axis=False)
    assert EvidentialTable([], columns=[valid]).columns[0]["scale"] == {"gradient": False, "axis": False}


def test_categorical_stacks_and_strip_keep_their_existing_color_semantics():
    for original in (col.stacked_bar("a", "b"), col.strip("form", colors={"W": "blue"})):
        with pytest.raises(ValueError, match="numeric mark"):
            original.gradient(scale="viridis")
    with pytest.raises(ValueError, match="mutually exclusive"):
        col.bar("x", color="red").gradient(scale="viridis")
