"""The ``col`` builder and the ``settings`` helper."""

from __future__ import annotations

from collections.abc import Mapping

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
