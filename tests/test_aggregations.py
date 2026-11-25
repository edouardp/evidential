from __future__ import annotations

import statistics

import pytest

from evidential import BUILTIN_AGGREGATIONS, resolve_aggregation
from evidential.aggregations import apply_aggregations, weighted_mean_values


@pytest.fixture()
def summaries():
    return [
        {"render_type": "cell_data", "__ancestors": ["USA"], "revenue": 100, "orders": 1, "weight": 1},
        {"render_type": "cell_data", "__ancestors": ["USA"], "revenue": 250, "orders": 2, "weight": 3},
        {"render_type": "cell_data", "__ancestors": ["Canada"], "revenue": 80, "orders": 1, "weight": 1},
        {"render_type": "cell_data", "__ancestors": ["Canada"], "revenue": 120, "orders": 1, "weight": 1},
        {"render_type": "row_subtotal", "__group_key": "USA"},
        {"render_type": "row_total"},
    ]


def test_builtin_mean_from_detail_values(summaries):
    apply_aggregations(summaries, {"revenue": "mean"}, ["revenue"])
    assert summaries[-1]["revenue"] == pytest.approx(137.5)


def test_custom_callable_aggregation(summaries):
    apply_aggregations(summaries, {"revenue": max}, ["revenue"])
    assert summaries[-2]["revenue"] == summaries[-1]["revenue"] == 250


def test_aggregation_applies_to_all_measures(summaries):
    apply_aggregations(summaries, statistics.median, ["revenue", "orders"])
    assert summaries[-1]["revenue"] == pytest.approx(110)
    assert summaries[-1]["orders"] == 1


def test_weighted_mean(summaries):
    apply_aggregations(summaries, {"revenue": "weighted_mean"}, ["revenue"], {"revenue": "weight"})
    assert summaries[-1]["revenue"] == pytest.approx((100 + 250 * 3 + 80 + 120) / 6)


def test_unknown_aggregation_raises() -> None:
    with pytest.raises(ValueError):
        resolve_aggregation("bogus")


def test_builtin_registry_has_common_functions() -> None:
    for name in ("sum", "mean", "median", "min", "max", "count", "count_distinct"):
        assert name in BUILTIN_AGGREGATIONS


def test_weighted_mean_keeps_missing_values_and_weights_paired():
    details = [
        {"render_type": "cell_data", "value": value, "weight": weight}
        for value, weight in [(None, 100), (10, 1), (20, 1), (999, None)]
    ]
    rows = [*details, {"render_type": "row_total"}]
    apply_aggregations(rows, {"value": "weighted_mean"}, ["value"], {"value": "weight"})
    assert rows[-1]["value"] == pytest.approx(15)


@pytest.mark.parametrize("weights", [[], [1], [1, 1, 1]])
def test_weighted_mean_rejects_mismatched_lengths(weights: list[float]) -> None:
    with pytest.raises(ValueError, match="same length"):
        weighted_mean_values([10, 20], weights)


def test_subtotal_descendant_lookup_scales_with_details_not_group_count() -> None:
    lookups = 0

    class Record(dict):
        def get(self, key, default=None):
            nonlocal lookups
            if key == "__ancestors":
                lookups += 1
            return super().get(key, default)

    details = [Record(value=1, render_type="cell_data", __ancestors=[str(index // 5)]) for index in range(100)]
    summaries = [{"render_type": "row_subtotal", "__group_key": str(index)} for index in range(20)]
    rows = [*details, *summaries, {"render_type": "row_total"}]
    apply_aggregations(rows, {"value": "sum"}, ["value"])
    assert [row["value"] for row in summaries] == [5] * 20
    assert rows[-1]["value"] == 100
    assert lookups <= len(details), f"descendant lookup rescanned details {lookups} times"
