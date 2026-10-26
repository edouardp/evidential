"""Sparkline references share the public builder and mapping validation paths."""

import pytest

from evidential import EvidentialTable, col


def test_reference_is_shared_by_factory_fluent_mapping_and_updates():
    options = {"type": "area", "signed": True, "reference": 1, "reference_color": "gray"}
    for column in (
        col.sparkline("values", **options),
        col.array("values").sparkline(**options),
        {"name": "values", "viz": "sparkline", "sparkline_options": options},
    ):
        table = EvidentialTable([{"values": [0.8, 1.2]}], columns=[column])
        assert table.columns[0]["sparkline_options"] == options
        table.set_column("values", sparkline_options={"reference": 0})
        assert table.columns[0]["sparkline_options"]["reference"] == 0
    refined = col.sparkline("values", reference=1).sparkline(reference=0)
    assert refined["sparkline_options"]["reference"] == 0


@pytest.mark.parametrize("reference", [float("nan"), float("inf"), -float("inf")])
def test_reference_requires_a_finite_value(reference):
    with pytest.raises(TypeError, match="reference"):
        col.sparkline("values", reference=reference)
    table = EvidentialTable([], columns=[col.sparkline("values")])
    original = table.columns
    with pytest.raises(TypeError, match="reference"):
        table.set_column("values", sparkline_options={"reference": reference})
    assert table.columns == original


def test_reference_settings_cannot_silently_affect_change_sparklines():
    with pytest.raises(ValueError, match="reference does not apply"):
        col.sparkline("values", type="change", reference=1)
    with pytest.raises(ValueError, match="reference_color requires reference"):
        col.sparkline("values", reference_color="red")
    with pytest.raises(TypeError, match="reference"):
        col.sparkline("values", reference="100%")
