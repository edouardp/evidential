"""Measure subtotal overrides separately from SQL and widget construction."""

from __future__ import annotations

import argparse
import json
import platform
import statistics
from time import perf_counter
from typing import Any

from evidential.aggregations import apply_aggregations


def grouped_rows(groups: int, members: int = 10) -> list[dict[str, Any]]:
    if groups < 1 or members < 1:
        raise ValueError("groups and members must be positive")
    rows = []
    for group in range(groups):
        key = str(group)
        rows.extend(
            {"x": index, "y": index * 2, "render_type": "cell_data", "__ancestors": [key]} for index in range(members)
        )
        rows.append({"render_type": "row_subtotal", "__group_key": key})
    rows.append({"render_type": "row_total", "__group_key": "__total__"})
    return rows


def benchmark(groups: list[int], repeats: int = 3) -> dict[str, Any]:
    if repeats < 1:
        raise ValueError("repeats must be positive")
    results = []
    for count in groups:
        rows = grouped_rows(count)
        durations = []
        for _ in range(repeats):
            start = perf_counter()
            apply_aggregations(rows, {"x": "sum", "y": "mean"}, ["x", "y"])
            durations.append((perf_counter() - start) * 1000)
        results.append({"groups": count, "detail_rows": count * 10, "elapsed_ms": statistics.median(durations)})
    return {"runtime": platform.python_version(), "results": results}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--groups", type=int, nargs="+", default=[100, 500, 2000])
    arguments = parser.parse_args()
    print(json.dumps(benchmark(arguments.groups), indent=2))
