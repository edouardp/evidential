import pytest

from evidential.aggregations import apply_aggregations
from scripts.benchmark_aggregations import benchmark, grouped_rows


def test_benchmark_records_have_correct_subtotal_and_total_relationships() -> None:
    rows = grouped_rows(2, 3)
    apply_aggregations(rows, {"x": "sum", "y": "mean"}, ["x", "y"])
    subtotals = [row for row in rows if row["render_type"] == "row_subtotal"]
    assert [row["x"] for row in subtotals] == [3, 3]
    assert rows[-1]["x"] == 6
    assert rows[-1]["y"] == 2
    report = benchmark([2], repeats=1)
    assert report["results"][0]["detail_rows"] == 20
    with pytest.raises(ValueError, match="positive"):
        grouped_rows(0)
    with pytest.raises(ValueError, match="positive"):
        benchmark([2], repeats=0)
