from unittest.mock import patch

import pytest

from evidential import DimensionGrid


class CountingGrid(DimensionGrid):
    def _refresh(self):
        self.refreshes = getattr(self, "refreshes", 0) + 1
        super()._refresh()


@pytest.mark.parametrize("selected", [{}, {"dimension": ["A"]}])
def test_initialization_and_replacement_do_one_facet_pass(selected):
    grid = CountingGrid(
        [{"dimension": "A", "value": 1}, {"dimension": "B", "value": 2}],
        dimensions=["dimension"],
        metric="value",
        selected=selected,
    )
    assert grid.refreshes == 1
    for records in ([{"dimension": "B", "value": 3}], [{"dimension": "B", "value": 4}], []):
        previous = grid.refreshes
        grid.set_data(records)
        assert grid.refreshes == previous + 1
        assert grid.filtered == records
    grid.close()


def test_data_replacement_synchronizes_selection_and_facets_together():
    grid = CountingGrid(
        [{"dimension": "A"}, {"dimension": "B"}], dimensions=["dimension"], selected={"dimension": ["A"]}
    )
    sent = []
    with patch.object(grid, "send_state", side_effect=lambda keys: sent.append(set(keys))) as send:
        grid.set_data([{"dimension": "B"}])
    assert send.call_count == 1
    assert sent == [{"selected", "facets"}]
    grid.close()
