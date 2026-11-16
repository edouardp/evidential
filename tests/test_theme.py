"""One validated theme contract for tables, live updates and dimension grids."""

import pytest

from evidential import DimensionGrid, EvidentialTable, col, color, settings


@pytest.mark.parametrize("scheme", ["auto", "light", "dark"])
def test_scheme_round_trip_and_update(scheme):
    options = settings(color_scheme=scheme, adapt_colors=True)
    table = EvidentialTable([{"x": 1}], **options)
    assert table.options["color_scheme"] == scheme
    table.update_options(color_scheme="dark", adapt_colors=False)
    assert table.options["color_scheme"] == "dark"
    assert not table.options["adapt_colors"]
    grid = DimensionGrid([{"team": "A"}], dimensions=["team"], **options)
    assert all(grid.options[key] == value for key, value in options.items())


@pytest.mark.parametrize("options", [{"color_scheme": "night"}, {"adapt_colors": "yes"}])
def test_invalid_theme_options(options):
    for constructor in [settings, EvidentialTable]:
        with pytest.raises((ValueError, TypeError)):
            constructor(**options)
    with pytest.raises((ValueError, TypeError)):
        DimensionGrid([{"team": "A"}], dimensions=["team"], **options)


def test_colors_are_serializable_in_all_color_positions():
    neutral = color.theme("neutral", alpha=0.8)
    exact = color.fixed("tab:red")
    assert neutral == "theme:neutral/0.8"
    assert exact == "fixed:tab:red"
    table = EvidentialTable(
        [{"x": 1}],
        columns=[col.bar("x", color=exact), col.point("x").gradient(scale=["red", neutral, "blue"])],
        color_scheme="dark",
        adapt_colors=True,
    )
    assert table.columns[0]["encodings"][0]["color"] == exact
    assert table.columns[1]["encodings"][0]["gradient"]["color_scale"][1] == neutral
    assert settings(theme={"positive": "green"})["theme"]["positive"] == "green"


@pytest.mark.parametrize("value", [None, "", "  ", "fixed:red", "theme:neutral"])
def test_fixed_requires_a_literal(value):
    with pytest.raises(ValueError):
        color.fixed(value)


@pytest.mark.parametrize("alpha", [-1, 2, True, "0.5", float("nan"), float("inf")])
def test_semantic_alpha_is_validated(alpha):
    with pytest.raises(ValueError):
        color.theme("neutral", alpha=alpha)


def test_semantic_role_is_validated():
    with pytest.raises(ValueError, match="Unknown theme colour"):
        color.theme("chartreuse")


@pytest.mark.parametrize("source", ["auto", "nearest", "host"])
def test_theme_source_round_trip(source):
    table = EvidentialTable([{"name": "A"}], theme_source=source)
    grid = DimensionGrid([{"name": "A"}], theme_source=source)
    assert table.options["theme_source"] == grid.options["theme_source"] == source
    with pytest.raises((TypeError, ValueError)):
        settings(theme_source="page")


def test_custom_css_is_widget_owned_and_updateable():
    css = ".et-title {font-size:21px}"
    table = EvidentialTable([{"name": "A"}], css=css)
    assert table.options["css"] == css
    table.update_options(css=None)
    assert table.options["css"] is None
    assert DimensionGrid([{"name": "A"}], css=css).options["css"] == css
