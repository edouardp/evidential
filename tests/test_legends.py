"""Legend declarations share the canonical column path and stay immutable."""

import pytest

from evidential import EvidentialTable, col
from evidential.marks import rebind_measure


def test_legend_builder_and_raw_declarations_share_validation():
    stack = col.stacked_bar("storage", "requests", colors=["blue", "orange"])
    labels = {"storage": "Storage", "requests": "API calls"}
    keyed = stack.legend(labels)
    labels["storage"] = "Changed outside the builder"
    assert "legend" not in stack
    assert keyed["legend"] == {"storage": "Storage", "requests": "API calls"}
    for declaration in (keyed, dict(keyed)):
        table = EvidentialTable([{"storage": 12, "requests": 3}], columns=[declaration])
        assert table.columns[0]["legend"] == keyed["legend"]
    assert keyed.legend(False)["legend"] is False
    assert stack.legend()["legend"] is True


def test_legend_lists_are_copied_and_survive_composition():
    names = ["Actual", "Forecast"]
    column = col.bar("actual", color="navy").bar("forecast", color="grey").legend(names)
    names[0] = "Changed"
    assert column["legend"] == ["Actual", "Forecast"]
    assert column.title("Revenue").scale(domain=(0, 100))["legend"] == ["Actual", "Forecast"]
    strip = col.strip("form", colors={"W": "navy", "D": "grey", "L": "red"}).legend(
        {"W": "Win", "D": "Draw", "L": "Loss"}
    )
    assert strip["legend"]["D"] == "Draw"


@pytest.mark.parametrize(
    ("labels", "error", "message"),
    [
        ("yes", TypeError, "legend expects"),
        (1, TypeError, "legend expects"),
        (["One"], ValueError, "one label per"),
        (["One", 2], TypeError, "must be strings"),
        ({"typo": "One"}, ValueError, "Unknown legend"),
        ({"a": 3}, TypeError, "map source names"),
    ],
)
def test_legend_rejects_invalid_labels_for_builders_and_dicts(labels, error, message):
    column = col.stacked_bar("a", "b")
    with pytest.raises(error, match=message):
        column.legend(labels)
    with pytest.raises(error, match=message):
        EvidentialTable([{"a": 1, "b": 2}], columns=[{**column, "legend": labels}])


def test_legend_revalidates_after_changes_and_requires_fixed_categories():
    with pytest.raises(ValueError, match="one label per"):
        EvidentialTable([{"a": 1, "b": 2}], columns=[col.bar("a").legend(["A"]).bar("b")])
    with pytest.raises(ValueError, match="per-row colors"):
        col.bar("a", color="@fill").legend()
    with pytest.raises(ValueError, match="colors mapping"):
        col.strip("form").legend()
    with pytest.raises(ValueError, match="mark column"):
        EvidentialTable([{"a": 1}], columns=[{"name": "a", "legend": True}])
    assert col.bar("a", color="@fill").legend(False)["legend"] is False


def test_pivot_rebinding_preserves_custom_source_names():
    original = col.bar("sales").legend({"sales": "Sales"})
    rebound = rebind_measure(original, "sales", "2026.sales")
    assert rebound["legend"] == {"2026.sales": "Sales"}
    assert original["legend"] == {"sales": "Sales"}


def test_connecting_marks_can_be_omitted_and_switching_to_scalar_removes_the_key():
    column = col.range("low", "high").point("young").point("old").legend([None, "0–9", "80+"])
    assert column["legend"] == [None, "0–9", "80+"]
    assert column.legend({"low": None})["legend"] == {"low": None}
    assert "legend" not in column.chip()


def test_legend_outline_is_optional_typed_and_cleared_with_scalar_styles():
    original = col.stacked_bar("a", "b")
    assert original.legend()["legend_options"] == {"outline": False, "column_names": None}
    outlined = original.legend(outline=True)
    assert outlined["legend_options"] == {"outline": True, "column_names": None}
    assert "legend_options" not in original
    assert "legend_options" not in outlined.chip()
    table = EvidentialTable([{"a": 1, "b": 2}], columns=[outlined])
    assert table.columns[0]["legend_options"] == {"outline": True, "column_names": None}
    with pytest.raises(TypeError, match="outline"):
        original.legend(outline="yes")
    with pytest.raises(TypeError, match="outline"):
        EvidentialTable([{"a": 1, "b": 2}], columns=[{**outlined, "legend_options": {"outline": "yes"}}])


def test_legend_column_names_can_be_forced_hidden_or_reset_to_automatic():
    original = col.stacked_bar("a", "b").legend()
    assert original["legend_options"]["column_names"] is None
    assert original.legend(column_names=True)["legend_options"]["column_names"] is True
    assert original.legend(column_names=False)["legend_options"]["column_names"] is False
    assert original.legend(column_names=True).legend()["legend_options"]["column_names"] is None
    with pytest.raises(TypeError, match="column_names"):
        original.legend(column_names="yes")
