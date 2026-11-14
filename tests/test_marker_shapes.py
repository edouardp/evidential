"""One typed marker contract across points, repeated shapes and sparkline markers."""

from typing import get_args

import pytest

from evidential import EvidentialTable, MarkerShape, col

SHAPES = get_args(MarkerShape)


@pytest.mark.parametrize("shape", SHAPES)
def test_factory_fluent_array_and_named_points_share_shape_options(shape):
    declarations = [
        col.point("x", shape=shape, angle=-90, outline="black"),
        col.bar("x").point("y", shape=shape, angle=270, outline="black"),
        col.points("samples", shape=shape, angle=630, outline="black"),
        col.points(["x", "y"], shape=shape, angle=270, outline="black"),
        col.bar("x").points(["x", "y"], shape=shape, angle=270, outline="black"),
    ]
    for column in declarations:
        enc = column["encodings"][-1]
        assert (enc["shape"], enc["angle"], enc["outline"]) == (shape, 270, "black")
        table = EvidentialTable([{"x": 2, "y": 3, "samples": [1, 2]}], columns=[column])
        assert table.columns[0]["encodings"][-1] == enc
        table.set_column(column["name"], encodings=[enc])
        assert table.columns[0]["encodings"][0] == enc


@pytest.mark.parametrize("shape", SHAPES)
def test_symbols_shapes_ratings_and_sparkline_use_the_same_options(shape):
    for column in [
        col.symbols("n", shape=shape, angle=-45, outline=False),
        col.shapes("n", shape=shape, angle=-45, outline=False),
        col.number("n").symbols(shape=shape, angle=-45, outline=False),
        col.rating("n", shape=shape, angle=-45, outline=False),
    ]:
        spec = column.to_config()["symbol_options"]
        assert (spec["shape"], spec["angle"], spec["outline"]) == (shape, 315, False)
    for column in [
        col.sparkline("a", type="points", shape=shape, angle=-45, outline=False),
        col.array("a").sparkline(markers="ends", shape=shape, angle=-45, outline=False),
    ]:
        spec = column.to_config()["sparkline_options"]
        assert (spec["shape"], spec["angle"], spec["outline"]) == (shape, 315, False)


@pytest.mark.parametrize(
    "options",
    [
        {"shape": "octagon"},
        {"shape": "cross45"},
        {"shape": "line"},
        {"angle": float("nan")},
        {"angle": float("inf")},
        {"angle": True},
        {"angle": "45"},
        {"outline": ""},
        {"outline": []},
    ],
)
def test_invalid_marker_options_fail_consistently_and_updates_are_atomic(options):
    for factory in (
        lambda: col.point("x", **options),
        lambda: col.points("a", **options),
        lambda: col.number("x").symbols(**options),
        lambda: col.sparkline("a", type="points", **options),
    ):
        with pytest.raises((ValueError, TypeError)):
            factory()
    for config in [
        {"name": "x", "encodings": [{"kind": "point", "source": "x", **options}]},
        {"name": "x", "viz": "symbols", "symbol_options": options},
        {"name": "x", "viz": "sparkline", "sparkline_options": {"type": "points", **options}},
    ]:
        with pytest.raises((ValueError, TypeError)):
            EvidentialTable([], columns=[config])
        table = EvidentialTable([], columns=[col.number("x")])
        original = table.columns
        with pytest.raises((ValueError, TypeError)):
            table.set_column("x", **{key: value for key, value in config.items() if key != "name"})
        assert table.columns == original


@pytest.mark.parametrize("kind", ["bar", "range", "strip", "boxplot"])
def test_other_marks_reject_point_geometry(kind):
    with pytest.raises(ValueError, match="not supported"):
        EvidentialTable(
            [], columns=[{"name": "x", "encodings": [{"kind": kind, "source": "x", "high": "y", "shape": "star"}]}]
        )


def test_existing_point_defaults_are_unchanged_and_marker_options_are_immutable():
    assert col.point("x")["encodings"] == [{"kind": "point", "source": "x"}]
    original = col.number("x").symbols(shape="square", angle=20)
    refined = original.symbols(angle=45, outline=False)
    assert original["symbol_options"]["angle"] == 20
    assert refined["symbol_options"]["angle"] == 45
    for kind in ("bar", "change"):
        with pytest.raises(ValueError, match="points or line/area"):
            col.sparkline("a", type=kind, shape="star")
