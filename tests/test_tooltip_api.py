"""Tooltip overrides are immutable, typed, serializable and presentation-only."""

import pytest

from evidential import EvidentialTable, col, settings
from evidential.marks import rebind_measure


@pytest.mark.parametrize("builder", [col.text, col.number, col.bar, col.sparkline])
def test_tooltip_overrides_are_shared_by_scalar_and_graphic_columns(builder):
    original = builder("amount")
    for setting in (True, False, "Two lines\nMore detail", "@hover_text"):
        changed = original.tooltip(setting)
        assert "tooltip" not in original
        assert changed["tooltip"] == setting
        for declaration in (changed, dict(changed)):
            table = EvidentialTable([{"amount": 12, "hover_text": "Source\nProvisional"}], columns=[declaration])
            assert table.columns[0]["tooltip"] == setting
            assert table.raw[0]["hover_text"] == "Source\nProvisional"
        assert changed.tooltip()["tooltip"] is True


@pytest.mark.parametrize("value", [None, 1, [], {}, 1.2])
def test_invalid_tooltip_types_fail_for_builders_and_raw_specs(value):
    with pytest.raises(TypeError, match="tooltip"):
        col.number("value").tooltip(value)
    # Canonical optional settings accept None as an unset field.
    if value is not None:
        with pytest.raises((ValueError, TypeError), match="tooltip"):
            EvidentialTable([{"value": 1}], columns=[{"name": "value", "tooltip": value}])


def test_tooltip_binding_needs_a_field_and_rebinds_without_changing_literals():
    for column in (col.number("value"), col.bar("value")):
        with pytest.raises(ValueError, match="field name"):
            column.tooltip("@")
        with pytest.raises(ValueError, match="field name"):
            EvidentialTable([{"value": 1}], columns=[{**column, "tooltip": "@"}])
        assert rebind_measure(column.tooltip("@value"), "value", "2024.value")["tooltip"] == "@2024.value"
        assert rebind_measure(column.tooltip("value"), "value", "2024.value")["tooltip"] == "value"


def test_tooltip_delays_are_seconds_and_column_overrides_are_immutable():
    frame = settings(tooltips={"delay": 0.8, "text_delay": 1.5})
    original = col.bar("value").tooltip(delay=0.2)
    overridden = original.tooltip("@hint", text_delay=0)
    assert original["tooltip_options"] == {"delay": 0.2}
    assert overridden["tooltip_options"] == {"delay": 0.2, "text_delay": 0}
    table = EvidentialTable([{"value": 1, "hint": "Note"}], columns=[overridden], settings=frame)
    assert table.options["tooltips"] == {"delay": 0.8, "text_delay": 1.5}
    assert table.columns[0]["tooltip_options"] == {"delay": 0.2, "text_delay": 0}


@pytest.mark.parametrize("value", [-1, True, "0.8", float("inf"), float("nan")])
def test_invalid_delays_fail_in_every_public_configuration_path(value):
    for key in ("delay", "text_delay"):
        with pytest.raises((TypeError, ValueError), match=key):
            col.bar("value").tooltip(**{key: value})
        with pytest.raises((TypeError, ValueError), match=key):
            settings(tooltips={key: value})
        with pytest.raises((TypeError, ValueError), match=key):
            EvidentialTable([{"value": 1}], columns=[{"name": "value", "tooltip_options": {key: value}}])
