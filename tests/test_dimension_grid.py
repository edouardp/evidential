"""Facet aggregation, selection semantics and safe linked queries."""

import duckdb
import pandas as pd
import pyarrow as pa
import pytest
import traitlets

from evidential import DimensionGrid

RECORDS = [
    {"service": "RDS", "usage": "Storage", "region": "EU", "cost": 12},
    {"service": "RDS", "usage": "Storage", "region": "US", "cost": 8},
    {"service": "RDS", "usage": "Backup", "region": "EU", "cost": None},
    {"service": "EC2", "usage": "Compute", "region": "US", "cost": 30},
    {"service": "EC2", "usage": "Storage", "region": None, "cost": -2},
]


def items(grid, name):
    return {row["value"]: row["metric"] for facet in grid.facets if facet["name"] == name for row in facet["items"]}


@pytest.mark.parametrize("container", [list, pd.DataFrame, pa.Table.from_pylist])
def test_infers_string_dimensions_and_normalizes_data(container):
    grid = DimensionGrid(container(RECORDS), metric="cost")
    assert [facet["name"] for facet in grid.facets] == ["service", "usage", "region"]
    assert items(grid, "service") == {"EC2": 28, "RDS": 20}
    assert "rows" not in grid.get_state()  # Only aggregates cross the wire.
    assert grid.raw == RECORDS


def test_hierarchical_selection_constrains_other_dimensions_but_keeps_alternatives():
    grid = DimensionGrid(RECORDS, metric="cost")
    grid.selected = {"service": ["RDS"]}
    assert items(grid, "usage") == {"Storage": 20, "Backup": 0}
    assert items(grid, "service") == {"EC2": 28, "RDS": 20}
    assert len(grid.filtered) == 3
    grid.selected = {"service": ["RDS"], "region": ["EU"]}
    assert items(grid, "service") == {"RDS": 12}
    assert items(grid, "usage") == {"Storage": 12, "Backup": 0}
    assert len(grid.filtered) == 2


def test_multiple_is_or_within_dimension_and_and_between_dimensions():
    grid = DimensionGrid(RECORDS, multiple=True)
    grid.selected = {"service": ["RDS", "EC2", "RDS"], "region": ["EU", None]}
    assert grid.selected["service"] == ["RDS", "EC2"]
    assert len(grid.filtered) == 3
    grid.clear()
    assert grid.filtered == RECORDS


@pytest.mark.parametrize(
    ("aggregate", "metric", "expected"),
    [
        ("count", None, 3),
        ("count", "cost", 2),
        ("sum", "cost", 20),
        ("mean", "cost", 10),
        ("min", "cost", 8),
        ("max", "cost", 12),
    ],
)
def test_aggregates_ignore_null_metrics(aggregate, metric, expected):
    grid = DimensionGrid(RECORDS, dimensions={"service": "AWS service"}, metric=metric, aggregate=aggregate)
    assert items(grid, "service")["RDS"] == expected
    assert grid.facets[0]["title"] == "AWS service"


def test_incompatible_selection_is_retained_and_can_be_cleared():
    grid = DimensionGrid(RECORDS, metric="cost", selected={"service": ["RDS"], "usage": ["Compute"]})
    assert grid.filtered == []
    assert items(grid, "usage")["Compute"] is None
    assert items(grid, "service")["RDS"] is None
    grid.clear()
    assert len(grid.filtered) == 5


def test_where_quotes_identifiers_binds_values_and_handles_nulls():
    name = 'odd"field'
    data = [{name: "O'Reilly", "other": 1}, {name: None, "other": 2}, {name: "x", "other": 3}]
    grid = DimensionGrid(data, dimensions=[name], multiple=True)
    assert grid.where() == ("TRUE", [])
    grid.selected = {name: ["O'Reilly", None]}
    statement, params = grid.where()
    assert "O'Reilly" not in statement
    with duckdb.connect() as con:
        con.register("source", pd.DataFrame(data))
        result = con.execute(f"SELECT * FROM source WHERE {statement}", params).fetchall()
    assert result == [("O'Reilly", 1), (None, 2)]


def test_set_data_prunes_absent_selections_updates_metrics_and_is_atomic_on_error():
    grid = DimensionGrid(RECORDS, metric="cost", selected={"service": ["RDS"]})
    grid.set_data([{"service": "EC2", "usage": "Compute", "region": "US", "cost": 99}])
    assert grid.selected == {}
    assert items(grid, "service") == {"EC2": 99}
    with pytest.raises(TypeError, match="numeric"):
        grid.set_data([{"service": "EC2", "cost": "invalid"}])
    assert items(grid, "service") == {"EC2": 99}
    grid.set_data([])
    assert grid.filtered == []
    assert all(facet["items"] == [] for facet in grid.facets)


def test_source_and_returned_snapshots_are_detached():
    source = [{"name": "A", "metadata": {"value": 1}}]
    grid = DimensionGrid(source, dimensions=["name"])
    source[0]["name"] = "changed"
    grid.raw[0]["metadata"]["value"] = 99
    grid.filtered[0]["name"] = "changed"
    assert grid.raw == [{"name": "A", "metadata": {"value": 1}}]


@pytest.mark.parametrize(
    "selection",
    [
        {"unknown": ["RDS"]},
        {"service": "RDS"},
        {"service": ["bad"]},
        {"service": ["RDS", "EC2"]},
        {"service": [["RDS"]]},
    ],
)
def test_invalid_selection_is_rejected_without_changing_the_grid(selection):
    grid = DimensionGrid(RECORDS, multiple=False)
    before = grid.facets
    with pytest.raises(traitlets.TraitError):
        grid.selected = selection
    assert grid.selected == {}
    assert grid.facets == before


@pytest.mark.parametrize(
    "kwargs",
    [
        {"dimensions": []},
        {"dimensions": "service"},
        {"dimensions": ["missing"]},
        {"metric": "missing"},
        {"aggregate": "mean"},
        {"aggregate": "invalid"},
        {"height": 0},
        {"dimension_width": True},
        {"multiple": "yes"},
    ],
)
def test_invalid_configuration_fails_early(kwargs):
    with pytest.raises((TypeError, ValueError)):
        DimensionGrid(RECORDS, **kwargs)


def test_all_categories_are_available_for_search_not_only_the_top_ten():
    grid = DimensionGrid([{"service": f"Service {index:03}", "cost": index} for index in range(230)], metric="cost")
    assert len(grid.facets[0]["items"]) == 230
    assert grid.facets[0]["items"][-1]["value"] == "Service 000"


def test_boolean_and_numeric_categories_have_distinct_identity():
    grid = DimensionGrid([{"value": True}, {"value": 1}, {"value": "1"}], dimensions=["value"])
    grid.selected = {"value": [True]}
    assert grid.filtered == [{"value": True}]


def test_json_numeric_identity_and_non_numeric_count_metric():
    grid = DimensionGrid(
        [{"value": 1, "name": "A"}, {"value": 1.0, "name": None}],
        dimensions=["value"],
        metric="name",
        aggregate="count",
    )
    assert len(grid.facets[0]["items"]) == 1
    assert grid.facets[0]["items"][0]["metric"] == 1
    grid.selected = {"value": [1.0]}
    assert len(grid.filtered) == 2


def test_multiple_selection_is_enabled_by_default():
    grid = DimensionGrid(RECORDS)
    grid.selected = {"service": ["RDS", "EC2"]}
    assert grid.options["multiple"] is True
    assert grid.filtered == RECORDS
