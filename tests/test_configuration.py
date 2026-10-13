from copy import deepcopy

import ipywidgets
import pytest

from evidential import EvidentialTable, make_column
from evidential.configuration import TABLE_DEFAULTS, ColumnOptions, TableOptions, validate_options


def test_defaults_have_one_schema_and_pass_validation() -> None:
    assert set(TABLE_DEFAULTS) == set(TableOptions.__annotations__)
    validate_options(TABLE_DEFAULTS, TableOptions, "table")
    validate_options(make_column("value"), ColumnOptions, "column")


@pytest.mark.parametrize("options", [{"page_szie": 10}, {"theme": {"bakground": "red"}}])
def test_unknown_table_options_are_rejected_with_context(options) -> None:
    with pytest.raises(ValueError, match="Unknown table"):
        EvidentialTable([], **options)


def test_unknown_update_does_not_modify_widget_state() -> None:
    table = EvidentialTable([{"value": 1}])
    before = dict(table.options)
    with pytest.raises(ValueError, match="did you mean 'page_size'"):
        table.update_options(page_szie=5)
    assert table.options == before


@pytest.mark.parametrize(
    "config",
    [
        {"fnt": "Arial"},
        {"color_options": {"minn": 0}},
        {"contentType": "bogus"},
    ],
)
def test_unknown_column_options_rejected_in_all_entry_points(config) -> None:
    with pytest.raises(ValueError, match="Unknown"):
        EvidentialTable([{"value": 1}], column_config={"value": config})
    table = EvidentialTable([{"value": 1}])
    before = deepcopy(table.columns)
    with pytest.raises(ValueError, match="Unknown"):
        table.set_column("value", **config)
    assert table.columns == before
    with pytest.raises(ValueError, match="Unknown"):
        table.set_data([{"value": 2}], column_config={"value": config})


@pytest.mark.parametrize(
    "options",
    [
        {"page_size": "ten"},
        {"search": "yes"},
        {"freeze_columns": True},
        {"row_shading": [1, 2, 3]},
        {"default_sort": {"direction": "sideways"}},
    ],
)
def test_invalid_table_values_are_rejected(options) -> None:
    with pytest.raises(TypeError, match="table"):
        EvidentialTable([], **options)


def test_nested_options_validate_values_and_preserve_aliases() -> None:
    with pytest.raises(TypeError, match="color_options.min"):
        make_column("value", color_options={"min": "zero"})
    with pytest.raises(ValueError, match="color_stops"):
        make_column("value", color_options={"color_stops": [{"value": 0}]})
    table = EvidentialTable([{"value": 1}], column_config={"value": {"contentType": "bar", "barColor": "red"}})
    assert table.columns[0]["bar_options"] == {"bar_color": "red"}


def test_pair_options_accept_lists_but_reject_wrong_shapes() -> None:
    table = EvidentialTable([], row_shading=[2, 3])
    assert table.options["row_shading"] == [2, 3]
    table.set_column("value", neutral_range=[-1, 1])
    assert table.columns[0]["delta_options"]["neutral_range"] == [-1, 1]
    with pytest.raises(TypeError, match="neutral_range"):
        table.set_column("value", neutral_range=[-1, 0, 1])
    with pytest.raises(TypeError, match="column.bar_options"):
        table.set_column("value", bar_options="bad")


def test_widget_traits_still_pass_through() -> None:
    layout = ipywidgets.Layout(width="400px")
    table = EvidentialTable([], layout=layout)
    assert table.layout is layout
