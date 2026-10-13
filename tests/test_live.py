from __future__ import annotations

import sys
from types import SimpleNamespace

import duckdb
import pytest

from evidential import LiveEvidentialTable, query_values
from evidential.duck import connect


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


@pytest.mark.skipif(sys.version_info < (3, 14), reason="t-strings require Python 3.14")
def test_real_t_string_control_updates(con) -> None:
    control = FakeControl(2)
    template = eval("t'SELECT {control} AS value'", {"control": control})
    live = LiveEvidentialTable(con, template, bind_controls=True)
    assert live.rows == [{"value": 2}]
    control.update(3)
    assert live.rows == [{"value": 3}]
    live.close()


@pytest.fixture()
def con() -> duckdb.DuckDBPyConnection:
    connection = connect(extensions=())
    connection.execute(
        """
        CREATE TABLE t AS SELECT * FROM (VALUES
            (1, 10.0), (2, 20.0), (3, 30.0)
        ) AS v(a, amount)
        """
    )
    return connection


def test_live_table_runs_parameterised_query(con: duckdb.DuckDBPyConnection) -> None:
    live = LiveEvidentialTable(con, "SELECT a FROM t WHERE a >= {min_a}", params={"min_a": 2})
    assert live.rows == [{"a": 2}, {"a": 3}]
    assert live.sql == "SELECT a FROM t WHERE a >= ?"


def test_live_table_reruns_when_bound_control_changes(con: duckdb.DuckDBPyConnection) -> None:
    control = FakeControl(2)
    live = LiveEvidentialTable(
        con,
        "SELECT a FROM t WHERE a >= $min_a",
        params={"min_a": control},
        bind_controls=True,
    )
    assert [row["a"] for row in live.rows] == [2, 3]

    control.update(3)
    assert [row["a"] for row in live.rows] == [3]


def test_live_table_preserves_column_config_between_runs(con: duckdb.DuckDBPyConnection) -> None:
    live = LiveEvidentialTable(
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
    live = LiveEvidentialTable(con, template)
    assert [row["a"] for row in live.rows] == [3]


def test_live_table_binds_t_string_control(con: duckdb.DuckDBPyConnection) -> None:
    control = FakeControl(2)
    template = FakeTemplate(["SELECT a FROM t WHERE a >= ", ""], [control])
    live = LiveEvidentialTable(con, template, bind_controls=True)
    assert [row["a"] for row in live.rows] == [2, 3]
    control.update(3)
    assert [row["a"] for row in live.rows] == [3]


def test_unknown_parameter_raises(con: duckdb.DuckDBPyConnection) -> None:
    with pytest.raises(KeyError):
        LiveEvidentialTable(con, "SELECT a FROM t WHERE a >= {missing}", params={})


def test_query_values(con: duckdb.DuckDBPyConnection) -> None:
    assert query_values(con, "SELECT a FROM t ORDER BY a") == [1, 2, 3]


def test_set_controls(con: duckdb.DuckDBPyConnection) -> None:
    control = FakeControl(1)
    live = LiveEvidentialTable(con, "SELECT a FROM t WHERE a >= {min_a}", params={"min_a": control})
    live.set_controls(min_a=2)
    assert [row["a"] for row in live.rows] == [2, 3]


def test_run_toggles_loading(con: duckdb.DuckDBPyConnection) -> None:
    live = LiveEvidentialTable(con, "SELECT a FROM t WHERE a >= {min_a}", params={"min_a": 1})
    seen: list[bool] = []
    live.observe(lambda change: seen.append(change["new"]), names="loading")
    live.run(params={"min_a": 2})
    assert seen == [True, False]
    assert live.loading is False


def test_rerun_does_not_reassign_unchanged_columns(con: duckdb.DuckDBPyConnection) -> None:
    live = LiveEvidentialTable(con, "SELECT a, amount FROM t WHERE a >= {min_a}", params={"min_a": 1})
    changes: list[str] = []
    live.observe(lambda change: changes.append(change["name"]), names="columns")
    live.run(params={"min_a": 2})
    assert changes == []  # column structure is unchanged, so only rows re-render


def test_binding_supports_real_ipywidgets_and_unsubscribes(con) -> None:
    import ipywidgets

    control = ipywidgets.IntSlider(value=1)
    replacement = ipywidgets.IntSlider(value=2)
    live = LiveEvidentialTable(con, "SELECT {x} AS x", params={"x": control}, bind_controls=True)
    control.value = 3
    assert live.rows == [{"x": 3}]
    live.run(params={"x": replacement})
    changes = []
    live.observe(lambda change: changes.append(change["new"]), names="loading")
    control.value = 4
    assert changes == []
    live.close()
    replacement.value = 5
    assert changes == []
    control.close()
    replacement.close()


def test_replaced_private_control_is_unbound(con) -> None:
    original, replacement = FakeControl(1), FakeControl(2)
    live = LiveEvidentialTable(con, "SELECT {x} AS x", params={"x": original}, bind_controls=True)
    live.run(params={"x": replacement})
    assert original._on_change is None
    live.close()
    assert replacement._on_change is None


def test_parameter_placeholders_ignore_sql_literals_and_comments(con) -> None:
    sql = "SELECT '{literal}' AS a, $$ $quoted $$ AS b, {x} AS c -- {comment}\n/* $block */"
    live = LiveEvidentialTable(con, sql, params={"x": 2})
    assert live.rows == [{"a": "{literal}", "b": " $quoted ", "c": 2}]
