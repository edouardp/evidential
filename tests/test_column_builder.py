"""The ``col`` builder and the ``settings`` helper."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import pytest

from evidential import EvidentialTable, col, settings

ROWS = [{"city": "NYC", "sales": 4200.0, "status": "ok", "change": 0.12, "trend": [1, 2, 3]}]


def test_column_builder_chains_are_immutable() -> None:
    base = col.number("sales")
    styled = base.fmt("usd0").bar(color="#93c5fd", fit_to_data=True)
    assert dict(base) == {"name": "sales", "type": "number"}
    assert styled["viz"] == "bar"
    assert styled["bar_options"] == {"bar_color": "#93c5fd", "fit_to_data": True}
    assert "viz" not in base


def test_column_builder_is_a_mapping() -> None:
    column = col.text("city").title("City").group("Location")
    assert isinstance(column, Mapping)
    assert dict(column) == {"name": "city", "type": "string", "title": "City", "column_group": "Location"}


def test_factories_give_sensible_types() -> None:
    assert col.text("x")["type"] == "string"
    assert col.number("x")["type"] == "number"
    assert col.boolean("x")["type"] == "boolean"
    assert col.date("x")["type"] == "date"
    assert col.sparkline("x")["type"] == "array"
    assert col.chip("x")["type"] == "string"
    assert col.delta("x")["type"] == "number"


def test_kind_factories_set_a_baseline() -> None:
    assert dict(col.integer("orders")) == {"name": "orders", "type": "number", "fmt": "num0"}
    assert col.percent("share")["fmt"] == "pct"
    assert col.percent("share", decimals=2)["fmt"] == "pct2"
    assert col.percent("rate", whole=True)["fmt"] == '0.0"%"'
    assert col.percent("rate", whole=True, decimals=0)["fmt"] == '0"%"'
    assert col.currency("sales")["fmt"] == "usd"
    assert col.currency("sales", code="EUR", decimals=2)["fmt"] == "eur2"
    assert col.flag("country")["fmt"] == "flag"
    assert col.bar("sales", color="#111")["viz"] == "bar"
    assert col.color("sales")["viz"] == "color"
    assert col.url("link")["link"] == "link"


def test_sparkline_factory_routes_its_options() -> None:
    # Regression: the factory used to drop x/y/color/fit_to_data at the top level
    # (where color became font_color and fit_to_data landed in bar_options).
    spec = dict(col.sparkline("trend", type="area", x="date", y="trips", color="#53768a", fit_to_data=True))
    assert spec["sparkline_options"] == {
        "type": "area",
        "x": "date",
        "y": "trips",
        "color": "#53768a",
        "fit_to_data": True,
    }
    assert "color" not in spec and "fit_to_data" not in spec


def test_kind_factories_validate_and_chain() -> None:
    with pytest.raises(ValueError, match="unknown currency code"):
        col.currency("sales", code="xyz")
    with pytest.raises(ValueError, match="percent decimals"):
        col.percent("share", decimals=9)
    chained = col.currency("sales", code="gbp").bar(color="#111")
    assert (chained["fmt"], chained["viz"]) == ("gbp", "bar")


def test_columns_accept_the_builder() -> None:
    table = EvidentialTable(
        ROWS,
        columns=[col.text("city"), col.number("sales").fmt("usd0").bar(color="#111")],
    )
    assert [column["name"] for column in table.columns] == ["city", "sales"]
    assert table.columns[1]["fmt"] == "usd0"
    assert table.columns[1]["viz"] == "bar"


def test_column_config_accepts_the_builder() -> None:
    table = EvidentialTable(ROWS, column_config={"sales": col.number("sales").fmt("usd2")})
    sales = next(column for column in table.columns if column["name"] == "sales")
    assert (sales["type"], sales["fmt"]) == ("number", "usd2")


def test_settings_bundle_splats_and_overrides() -> None:
    report = settings(title="Sales", page_size=5, border=False)
    assert report == {"title": "Sales", "page_size": 5, "border": False}

    table = EvidentialTable(ROWS, **report)
    assert (table.options["title"], table.options["border"]) == ("Sales", False)

    overridden = EvidentialTable(ROWS, settings=report, title="This month")
    assert overridden.options["title"] == "This month"
    assert overridden.options["page_size"] == 5


def test_unknown_options_suggest_a_fix() -> None:
    with pytest.raises(ValueError, match="did you mean 'border'"):
        settings(borderr=False)
    with pytest.raises(ValueError, match="did you mean 'bar_options'"):
        EvidentialTable(ROWS, column_config={"sales": {"barOption": {}}})


def test_subcolumns_label_every_member() -> None:
    group = col.subcolumns("Latest", [col.number("sales").fmt("num1"), col.text("change")])
    assert isinstance(group, Sequence)
    assert group.kind == "subcolumns" and group.label == "Latest"
    assert [column["subcolumn_group"] for column in group] == ["Latest", "Latest"]
    assert repr(group).startswith("col.subcolumns('Latest', [")


def test_group_builder_names_a_spanner() -> None:
    table = EvidentialTable(
        ROWS,
        columns=[
            col.text("city"),
            col.group("Economy", [col.number("sales"), col.number("change")], highlight="#eef2ff"),
        ],
    )
    assert [column["name"] for column in table.columns] == ["city", "sales", "change"]
    by_name = {column["name"]: column for column in table.columns}
    assert by_name["sales"]["column_group"] == "Economy"
    assert by_name["sales"]["highlight"] == "#eef2ff"


def test_groups_nest_and_accept_names_and_mappings() -> None:
    group = col.group(
        "Economy",
        [col.subcolumns("Latest", [col.number("sales")]), "change", {"name": "cpi", "type": "number"}],
    )
    assert [column["name"] for column in group] == ["sales", "change", "cpi"]
    assert group[0]["subcolumn_group"] == "Latest"
    assert group[0]["column_group"] == "Economy"


def test_group_members_cannot_lose_the_label() -> None:
    table = EvidentialTable(
        ROWS,
        columns=[col.subcolumns("Latest", [col.number("sales"), col.text("change")])],
    )
    assert all(column["subcolumn_group"] == "Latest" for column in table.columns)


def test_group_rejects_non_columns() -> None:
    with pytest.raises(TypeError, match="expected a column name"):
        col.group("G", [42])


def test_temporal_kinds_and_relative() -> None:
    assert col.date("day")["type"] == "date"
    assert "fmt" not in col.date("day")
    assert col.time("clock")["fmt"] == "hms"
    assert col.datetime("stamp")["fmt"] == "datetime"
    assert col.datetime("stamp", relative=True)["relative"] is True
    assert col.date("day").relative("day")["relative"] == "day"
    assert col.datetime("stamp", relative="hour")["relative"] == "hour"

    table = EvidentialTable(ROWS, columns=[col.date("day", relative=True)])
    assert (table.columns[0]["type"], table.columns[0]["relative"]) == ("date", True)


def test_relative_rejects_an_unknown_unit() -> None:
    with pytest.raises(TypeError, match="relative"):
        EvidentialTable(ROWS, columns=[{"name": "day", "type": "date", "relative": "fortnight"}])


def test_auto_keeps_the_inferred_definition() -> None:
    rows = [{"city": "NYC", "pop": 1234, "year": "2020"}]
    table = EvidentialTable(rows, columns=["city", col.auto("pop"), col.auto("year")])
    by_name = {column["name"]: column for column in table.columns}
    assert by_name["pop"]["type"] == "number"
    assert by_name["pop"]["fmt"] == "num0"  # the inferred integer format survives
    assert by_name["city"]["type"] == "string"  # a bare name infers too

    refined = EvidentialTable(rows, columns=[col.auto("pop").bar(color="#111")])
    assert (refined.columns[0]["type"], refined.columns[0]["viz"]) == ("number", "bar")

    patched = EvidentialTable(rows, column_config={"pop": col.auto("pop").fmt("usd0")})
    pop = next(column for column in patched.columns if column["name"] == "pop")
    assert (pop["type"], pop["fmt"]) == ("number", "usd0")


def test_auto_alias_wins_over_the_inferred_default() -> None:
    table = EvidentialTable(
        [{"x": 1}],
        columns=[{"name": "x", "redNegatives": True}],
    )
    assert table.columns[0]["red_negatives"] is True


def test_neg_marks_and_brackets_negatives() -> None:
    assert col.currency("profit").neg()["red_negatives"] is True
    spec = col.currency("profit").neg(color="#b91c1c", bracket=True)
    assert spec["negative_color"] == "#b91c1c"
    assert spec["bracket_negatives"] is True
    assert "bracket_negatives" not in col.currency("profit").neg()


def test_merge_names_a_cols_merge_spec() -> None:
    from evidential import cols_merge_range

    spec = cols_merge_range("low", "high", fmt="num0", title="Range")
    assert "name" not in spec
    merged = col.merge("range", spec)
    assert merged["name"] == "range"
    assert merged["title"] == "Range"


def test_grouped_helpers_accept_the_builder() -> None:
    import duckdb

    from evidential import grouped_table

    connection = duckdb.connect()
    connection.execute("CREATE TABLE t AS SELECT * FROM (VALUES ('a', 1, 10), ('b', 2, 20)) AS v(g, n, sales)")
    table = grouped_table(
        connection,
        "SELECT g, n, sales FROM t",
        dimensions=["g"],
        measures=["count(*) AS n", "sum(sales) AS sales"],
        dimension_config={"g": col.text("g", title="Group")},
        measure_config={"sales": col.currency("sales", decimals=0)},
    )
    by_name = {column["name"]: column for column in table.columns}
    assert by_name["g"]["title"] == "Group"
    assert by_name["sales"]["fmt"] == "usd0"
