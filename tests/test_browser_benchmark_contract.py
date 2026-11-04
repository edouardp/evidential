import pytest

from scripts.benchmark_browser import benchmark, scenario


@pytest.mark.parametrize("count,samples", [(0, 1), (39, 1), (120, 0), (120, -1)])
def test_browser_benchmark_rejects_unpageable_scenarios(count, samples):
    with pytest.raises(ValueError, match="navigation sample"):
        scenario(count, samples)


def test_browser_benchmark_uses_real_public_marks_and_auto_labels():
    data = scenario(40, 1)
    assert len(data["rows"]) == 40
    assert data["options"]["page_size"] == 20
    assert data["columns"][1]["encodings"][0]["label"]["auto"] is True
    assert data["columns"][2]["encodings"][0]["sources"] == ["a", "b"]
    with pytest.raises(ValueError, match="supported"):
        benchmark([], engine="invalid")
