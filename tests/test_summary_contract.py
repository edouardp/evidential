import json
from pathlib import Path

import pytest

from evidential import EvidentialTable, rows
from evidential.aggregations import summary_values

CASES = json.loads((Path(__file__).parent / "fixtures/summary-contract.json").read_text())


@pytest.mark.parametrize("case", CASES)
def test_python_and_browser_share_summary_behavior(case):
    assert summary_values(case["operation"], case["values"]) == case["expected"]
    records = [{"group": "A", "value": value} for value in case["values"]]
    table = EvidentialTable(records, row_layout=rows.group_by("group").summary(values={"value": case["operation"]}))
    assert table.row_layout["groups"][0]["summary"]["cells"]["value"]["value"] == case["expected"]


def test_numeric_summaries_reject_mixed_types_consistently():
    with pytest.raises(TypeError, match="numeric values"):
        summary_values("sum", [1, "2"])
