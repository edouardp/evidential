"""Sparkline styles have one public literal contract for builders and validation."""

from typing import Literal, get_args, get_origin, get_type_hints

import pytest

from evidential import Column, EvidentialTable, SparklineType, col
from evidential.configuration import SparklineOptions


def test_public_sparkline_literal_is_shared_by_both_builders_and_schema():
    assert get_origin(SparklineType) is Literal
    assert get_args(SparklineType) == ("line", "area", "bar", "points", "change")
    assert get_type_hints(col.sparkline)["type"] == SparklineType
    assert get_type_hints(Column.sparkline)["type"] == SparklineType | None
    assert get_type_hints(SparklineOptions)["type"] == SparklineType | None


@pytest.mark.parametrize("style", get_args(SparklineType))
def test_every_declared_style_is_accepted_by_factory_fluent_and_mapping(style):
    for column in (
        col.sparkline("values", type=style),
        col.array("values").sparkline(type=style),
        {"name": "values", "viz": "sparkline", "sparkline_options": {"type": style}},
    ):
        table = EvidentialTable([{"values": [1, 0, -1]}], columns=[column])
        assert table.columns[0]["sparkline_options"]["type"] == style


@pytest.mark.parametrize("style", ["bars", "scatter", 1, True])
def test_invalid_style_is_rejected_at_runtime_across_entry_points(style):
    with pytest.raises(TypeError, match="sparkline_options.type"):
        col.sparkline("values", type=style)
    with pytest.raises(TypeError, match="sparkline_options.type"):
        col.array("values").sparkline(type=style)
    with pytest.raises(TypeError, match="sparkline_options.type"):
        EvidentialTable(
            [{"values": [1]}],
            columns=[
                {
                    "name": "values",
                    "sparkline_options": {"type": style},
                }
            ],
        )
