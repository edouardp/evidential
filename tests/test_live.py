from __future__ import annotations

from types import SimpleNamespace

import duckdb
import pytest

from evidence_tables import LiveEvidenceTable, query_values
from evidence_tables.duck import connect


class FakeControl:
    """Stand-in for a Marimo/ipywidgets control."""

    def __init__(self, value: object) -> None:
        self.value = value
        self._on_change = None

    def update(self, value: object) -> None:
        self.value = value
        if callable(self._on_change):
            self._on_change(value)


class FakeTemplate:
    """Minimal PEP 750 t-string shape for Python < 3.14."""

    def __init__(self, strings: list[str], values: list[object]) -> None:
        self.strings = tuple(strings)
        self.interpolations = tuple(SimpleNamespace(value=value) for value in values)


@pytest.fixture()
def con() -> duckdb.DuckDBPyConnection:
    connection = connect()
    connection.execute(
        """
        CREATE TABLE t AS SELECT * FROM (VALUES
            (1, 10.0), (2, 20.0), (3, 30.0)
        ) AS v(a, amount)
        """
    )
    return connection


def test_live_table_runs_parameterised_query(con: duckdb.DuckDBPyConnection) -> None:
    live = LiveEvidenceTable(con, "SELECT a FROM t WHERE a >= {min_a}", params={"min_a": 2})
    assert live.rows == [{"a": 2}, {"a": 3}]
    assert live.sql == "SELECT a FROM t WHERE a >= ?"


def test_live_table_reruns_when_bound_control_changes(con: duckdb.DuckDBPyConnection) -> None:
    control = FakeControl(2)
    live = LiveEvidenceTable(
        con,
        "SELECT a FROM t WHERE a >= $min_a",
        params={"min_a": control},
        bind_controls=True,
    )
    assert [row["a"] for row in live.rows] == [2, 3]

    control.update(3)
    assert [row["a"] for row in live.rows] == [3]


def test_live_table_preserves_column_config_between_runs(con: duckdb.DuckDBPyConnection) -> None:
    live = LiveEvidenceTable(
        con,
        "SELECT a, amount FROM t WHERE a >= {min_a}",
        params={"min_a": 1},
        column_config={"amount": {"fmt": "usd0", "viz": "bar"}},
    )
    amount = next(column for column in live.columns if column["name"] == "amount")
    assert amount["fmt"] == "usd0"

    live.run(params={"min_a": 3})
    amount = next(column for column in live.columns if column["name"] == "amount")
    assert amount["fmt"] == "usd0"
    assert [row["a"] for row in live.rows] == [3]


def test_live_table_supports_t_string_interpolations(con: duckdb.DuckDBPyConnection) -> None:
    template = FakeTemplate(["SELECT a FROM t WHERE a >= ", ""], [3])
    live = LiveEvidenceTable(con, template)
    assert [row["a"] for row in live.rows] == [3]


def test_live_table_binds_t_string_control(con: duckdb.DuckDBPyConnection) -> None:
    control = FakeControl(2)
    template = FakeTemplate(["SELECT a FROM t WHERE a >= ", ""], [control])
    live = LiveEvidenceTable(con, template, bind_controls=True)
    assert [row["a"] for row in live.rows] == [2, 3]
    control.update(3)
    assert [row["a"] for row in live.rows] == [3]


def test_unknown_parameter_raises(con: duckdb.DuckDBPyConnection) -> None:
    with pytest.raises(KeyError):
        LiveEvidenceTable(con, "SELECT a FROM t WHERE a >= {missing}", params={})


def test_query_values(con: duckdb.DuckDBPyConnection) -> None:
    assert query_values(con, "SELECT a FROM t ORDER BY a") == [1, 2, 3]


def test_set_controls(con: duckdb.DuckDBPyConnection) -> None:
    control = FakeControl(1)
    live = LiveEvidenceTable(con, "SELECT a FROM t WHERE a >= {min_a}", params={"min_a": control})
    live.set_controls(min_a=2)
    assert [row["a"] for row in live.rows] == [2, 3]
