from __future__ import annotations

import datetime as dt
from decimal import Decimal

import pytest

from evidential import EvidentialTable, make_column
from evidential.duck import connect


def test_from_records_infers_columns() -> None:
    table = EvidentialTable(
        [
            {"city": "NYC", "trips": 120, "revenue": 4200.5, "when": dt.date(2024, 1, 1)},
            {"city": "LA", "trips": 90, "revenue": 3100.0, "when": dt.date(2024, 1, 2)},
        ]
    )
    types = {column["name"]: column["type"] for column in table.columns}
    assert types == {"city": "string", "trips": "number", "revenue": "number", "when": "date"}
    # Dates are serialized to ISO strings for JSON transport.
    assert table.rows[0]["when"] == "2024-01-01"


def test_arrow_types_drive_default_format_and_alignment() -> None:
    import pyarrow as pa

    arrow = pa.table(
        {
            "count": pa.array([1, 2, 3], pa.int64()),
            "ratio": pa.array([1.5, 2.25, 3.0], pa.float64()),
            "price": pa.array([Decimal("12.00"), Decimal("34.50"), Decimal("7.25")], pa.decimal128(10, 2)),
            "name": pa.array(["a", "b", "c"], pa.string()),
            "when": pa.array([dt.date(2024, 1, 1), None, dt.date(2024, 1, 3)], pa.date32()),
            "flag": pa.array([True, False, True], pa.bool_()),
            "items": pa.array([[1, 2], [3], [4]], pa.list_(pa.int32())),
            "meta": pa.array([{"a": 1}, {"a": 2}, {"a": 3}], pa.struct([("a", pa.int32())])),
        }
    )
    columns = {column["name"]: column for column in EvidentialTable(arrow).columns}

    assert (columns["count"]["type"], columns["count"]["fmt"], columns["count"]["align"]) == (
        "number",
        "num0",
        "right",
    )
    assert columns["ratio"].get("fmt") is None  # ambiguous precision -> auto-scaling
    assert columns["price"]["fmt"] == "num2"  # decimal scale is preserved
    assert (columns["name"]["type"], columns["name"]["align"]) == ("string", "left")
    assert columns["when"]["type"] == "date"
    assert columns["flag"]["type"] == "boolean"
    # Nested types must not be mistaken for their element type.
    assert columns["items"]["type"] == "array"
    assert columns["meta"]["type"] == "object"


def test_duckdb_result_types_default_formatting() -> None:
    import duckdb

    relation = duckdb.connect().sql("SELECT 1::INTEGER AS n, 2.5::DOUBLE AS x, 'a' AS s, DATE '2024-01-01' AS d")
    columns = {column["name"]: column for column in EvidentialTable(relation).columns}
    assert columns["n"]["fmt"] == "num0"  # integers are whole numbers
    assert columns["n"]["align"] == "right"
    assert columns["x"].get("fmt") is None  # floats keep auto-scaling
    assert (columns["s"]["type"], columns["s"]["align"]) == ("string", "left")
    assert columns["d"]["type"] == "date"


def test_duckdb_column_comments_become_header_info() -> None:
    import duckdb

    from evidential import duck

    con = duckdb.connect()
    con.execute("CREATE TABLE t (a INTEGER, b VARCHAR)")
    con.execute("COMMENT ON COLUMN t.a IS 'The a value'")

    # A table/view relation knows its name, so comments are read automatically,
    # including after .limit()/.filter()/.select().
    columns = {column["name"]: column for column in EvidentialTable(con.table("t")).columns}
    assert columns["a"]["info"] == "The a value"
    assert "info" not in columns["b"]
    assert EvidentialTable(con.table("t").limit(5)).columns[0]["info"] == "The a value"

    # Raw SQL becomes an unnamed relation; the helper is the explicit path.
    assert duck.column_comments(con, "t") == {"a": "The a value"}
    raw = {column["name"]: column for column in EvidentialTable(con.sql("SELECT a, b FROM t")).columns}
    assert "info" not in raw["a"]


def test_column_config_accepts_comment_and_description() -> None:
    table = EvidentialTable(
        [{"a": 1, "b": 2}],
        column_config={
            "a": {"comment": "The a value"},
            "b": {"description": "The b value"},
        },
    )
    columns = {column["name"]: column for column in table.columns}
    assert columns["a"]["info"] == "The a value"
    assert columns["b"]["info"] == "The b value"
    assert "comment" not in columns["a"]


def test_column_config_comment_overrides_an_inferred_description() -> None:
    import duckdb

    con = duckdb.connect()
    con.execute("CREATE TABLE t (a INTEGER)")
    con.execute("COMMENT ON COLUMN t.a IS 'Inferred from the database'")
    table = EvidentialTable(con.table("t"), column_config={"a": {"comment": "Overridden"}})
    assert table.columns[0]["info"] == "Overridden"


def test_delta_options_accept_top_level_config() -> None:
    table = EvidentialTable(
        [{"change": 0.05}],
        column_config={"change": {"viz": "delta", "neutral_range": "-0.1:0.1", "down_is_good": True}},
    )
    assert table.columns[0]["delta_options"] == {
        "neutral_range": "-0.1:0.1",
        "down_is_good": True,
    }


def test_column_sort_by_accepts_alias() -> None:
    table = EvidentialTable([{"a": 1, "b": 2}], column_config={"a": {"sort_by": "b"}})
    assert table.columns[0]["sort_by"] == "b"
    table2 = EvidentialTable([{"a": 1, "b": 2}], column_config={"a": {"sortBy": "b"}})
    assert table2.columns[0]["sort_by"] == "b"


def test_arrow_field_metadata_becomes_header_info() -> None:
    import pyarrow as pa

    schema = pa.schema(
        [
            pa.field("a", pa.int32(), metadata={b"comment": b"The a value"}),
            pa.field("b", pa.string(), metadata={"description": "The b value"}),  # str keys too
            pa.field("c", pa.int32()),
        ]
    )
    columns = {c["name"]: c for c in EvidentialTable(pa.table({"a": [1], "b": ["x"], "c": [2]}, schema=schema)).columns}
    assert columns["a"]["info"] == "The a value"
    assert columns["b"]["info"] == "The b value"
    assert "info" not in columns["c"]


def test_parquet_field_metadata_survives_to_info(tmp_path) -> None:
    import duckdb
    import pyarrow as pa
    import pyarrow.parquet as pq

    schema = pa.schema(
        [pa.field("a", pa.int32(), metadata={b"comment": b"The a value"})],
        metadata={b"description": b"A table"},
    )
    path = tmp_path / "t.parquet"
    pq.write_table(pa.table({"a": [1, 2]}, schema=schema), path)

    # PyArrow writes the Arrow schema into the file's ARROW:schema metadata, so
    # field comments survive a Parquet round-trip.
    assert EvidentialTable(pq.read_table(path)).columns[0]["info"] == "The a value"

    # DuckDB's read_parquet does not surface it.
    con = duckdb.connect()
    relation = con.sql(f"SELECT * FROM read_parquet('{path}')")
    assert "info" not in EvidentialTable(relation).columns[0]


def test_column_config_overrides() -> None:
    table = EvidentialTable(
        [{"revenue": 4200.5}],
        column_config={
            "revenue": {"fmt": "usd0", "viz": "bar", "align": "right"},
        },
    )
    column = table.columns[0]
    assert column["fmt"] == "usd0"
    assert column["viz"] == "bar"
    assert column["align"] == "right"


def test_table_options_round_trip() -> None:
    table = EvidentialTable([{"a": 1}], title="Hello", search=True, page_size=25)
    assert table.options["title"] == "Hello"
    assert table.options["search"] is True
    assert table.options["page_size"] == 25
    table.update_options(page_size=5)
    assert table.options["page_size"] == 5


def test_set_column_appends_and_updates() -> None:
    table = EvidentialTable([{"a": 1}])
    table.set_column("a", fmt="num0")
    table.set_column("b", type="number", viz="color")
    names = [column["name"] for column in table.columns]
    assert names == ["a", "b"]
    assert table.columns[1]["viz"] == "color"


def test_jsonify_handles_decimal_and_nan() -> None:
    table = EvidentialTable([{"x": Decimal("1.5"), "y": float("nan")}])
    assert table.rows[0]["x"] == 1.5
    assert table.rows[0]["y"] is None


def test_from_duckdb_relation() -> None:
    connection = connect()
    connection.execute("CREATE TABLE t AS SELECT 1 AS a, 'x' AS b")
    table = EvidentialTable.from_duckdb(connection, "SELECT * FROM t")
    assert table.rows == [{"a": 1, "b": "x"}]
    types = {column["name"]: column["type"] for column in table.columns}
    assert types == {"a": "number", "b": "string"}


def test_column_groups_assign_group_without_reordering() -> None:
    table = EvidentialTable(
        [{"month": "Jan", "cc": 1, "cash": 2, "other": 3}],
        column_groups={"Payment type": ["cc", "cash"]},
    )
    names = [column["name"] for column in table.columns]
    assert names == ["month", "cc", "cash", "other"]
    groups = {column["name"]: column.get("column_group") for column in table.columns}
    assert groups["cc"] == "Payment type"
    assert groups["cash"] == "Payment type"
    assert groups["month"] is None


def test_dotted_column_names_default_the_column_group() -> None:
    table = EvidentialTable([{"country": "US", "GDP Measure.gdp_nominal": 1.0, "GDP Measure.gdp_ppp": 2.0}])
    groups = {column["name"]: column.get("column_group") for column in table.columns}
    assert groups["GDP Measure.gdp_nominal"] == "GDP Measure"
    assert groups["GDP Measure.gdp_ppp"] == "GDP Measure"
    assert groups["country"] is None


def test_multi_level_dotted_name_becomes_a_nested_group() -> None:
    table = EvidentialTable([{"a.b.c": 1}])
    assert table.columns[0]["column_group"] == ["a", "b"]


def test_dotted_name_group_can_be_overridden() -> None:
    by_config = EvidentialTable([{"a.b": 1}], column_config={"a.b": {"column_group": "X"}})
    assert by_config.columns[0]["column_group"] == "X"
    by_mapping = EvidentialTable([{"a.b": 1}], column_groups={"Y": ["a.b"]})
    assert by_mapping.columns[0]["column_group"] == "Y"


def test_lone_dot_does_not_make_a_group() -> None:
    table = EvidentialTable([{".b": 1, "a.": 2}])
    assert [column.get("column_group") for column in table.columns] == [None, None]


def test_content_type_shorthand_maps_to_viz() -> None:
    table = EvidentialTable(
        [{"trend": [1, 2, 3]}],
        columns=[{"name": "trend", "content_type": "sparkbar"}],
    )
    column = table.columns[0]
    assert column["viz"] == "sparkline"
    assert column["sparkline_options"]["type"] == "bar"


def test_camelcase_column_aliases() -> None:
    table = EvidentialTable(
        [{"x": 1, "url": "https://example.com"}],
        columns=[
            {"name": "url", "contentType": "link"},
            {"name": "x", "colGroup": "Group A", "redNegatives": True, "description": "hint"},
        ],
    )
    url = next(column for column in table.columns if column["name"] == "url")
    assert url["link"] == "url"
    x = next(column for column in table.columns if column["name"] == "x")
    assert x["column_group"] == "Group A"
    assert x["red_negatives"] is True
    assert x["info"] == "hint"


def test_new_table_options_round_trip() -> None:
    table = EvidentialTable(
        [{"a": 1}],
        row_numbers=True,
        column_stats=True,
        compact=True,
        border=False,
        empty_message="Nothing here",
        empty_rows=5,
        default_sort={"column": "a", "direction": "asc"},
        row_conditional_colors="tint",
        header_color="#eeeeee",
    )
    assert table.options["row_numbers"] is True
    assert table.options["column_stats"] is True
    assert table.options["compact"] is True
    assert table.options["border"] is False
    assert table.options["empty_message"] == "Nothing here"
    assert table.options["empty_rows"] == 5
    assert table.options["default_sort"] == {"column": "a", "direction": "asc"}
    assert table.options["row_conditional_colors"] == "tint"
    assert table.options["header_color"] == "#eeeeee"


def test_column_stats_is_off_by_default() -> None:
    assert EvidentialTable([{"a": 1}]).options["column_stats"] is False


def test_chip_columns_are_centred_by_default() -> None:
    table = EvidentialTable([{"city": "A", "aqi": 1}], column_config={"aqi": {"viz": "chip"}})
    aqi = next(column for column in table.columns if column["name"] == "aqi")
    assert aqi["viz"] == "chip"
    assert aqi["align"] == "center"


def test_chip_align_can_be_overridden() -> None:
    table = EvidentialTable([{"aqi": 1}], column_config={"aqi": {"viz": "chip", "align": "right"}})
    assert table.columns[0]["align"] == "right"

    explicit = EvidentialTable([{"aqi": 1}], columns=[{"name": "aqi", "viz": "chip", "align": "left"}])
    assert explicit.columns[0]["align"] == "left"


def test_content_type_chip_sets_viz() -> None:
    table = EvidentialTable([{"aqi": 1}], columns=[{"name": "aqi", "content_type": "chip"}])
    assert table.columns[0]["viz"] == "chip"


def test_chip_min_width_options() -> None:
    table = EvidentialTable(
        [{"aqi": 1}],
        column_config={"aqi": {"viz": "chip", "chip_options": {"min_width": 72}}},
    )
    assert table.columns[0]["chip_options"] == {"min_width": 72}
    top_level = EvidentialTable(
        [{"aqi": 1}],
        column_config={"aqi": {"viz": "chip", "chip_min_width": 64}},
    )
    assert top_level.columns[0]["chip_options"] == {"min_width": 64}
    camel = EvidentialTable(
        [{"aqi": 1}],
        column_config={"aqi": {"viz": "chip", "chipMinWidth": 80}},
    )
    assert camel.columns[0]["chip_options"] == {"min_width": 80}


def test_select_option_and_selected_trait() -> None:
    table = EvidentialTable([{"country": "AUS"}], select="country")
    assert table.options["select"] == "country"
    assert table.selected is None
    table.selected = "AUS"
    assert table.selected == "AUS"
    preselect = EvidentialTable([{"country": "AUS"}], select="country", selected="AUS")
    assert preselect.selected == "AUS"


def test_column_highlight_round_trips() -> None:
    table = EvidentialTable([{"a": 1}], column_config={"a": {"highlight": "#eef2ff"}})
    assert table.columns[0]["highlight"] == "#eef2ff"
    camel = EvidentialTable([{"a": 1}], column_config={"a": {"highlightColor": "#eef2ff"}})
    assert camel.columns[0]["highlight"] == "#eef2ff"


def test_group_highlight_applies_to_every_column() -> None:
    table = EvidentialTable(
        [{"a": 1, "b": 2}],
        column_groups={"G": {"columns": ["a", "b"], "highlight": "#eef2ff"}},
    )
    assert all(column["highlight"] == "#eef2ff" for column in table.columns)


def test_column_highlight_wins_over_group_highlight() -> None:
    table = EvidentialTable(
        [{"a": 1, "b": 2}],
        column_groups={"G": {"columns": ["a", "b"], "highlight": "#eef2ff"}},
        column_config={"a": {"highlight": "#ffffff"}},
    )
    highlights = {column["name"]: column.get("highlight") for column in table.columns}
    assert highlights["a"] == "#ffffff"
    assert highlights["b"] == "#eef2ff"


def test_show_link_column() -> None:
    rows = [{"name": "A", "url": "https://example.com"}]
    hidden = EvidentialTable(rows, link="url")
    url = next(column for column in hidden.columns if column["name"] == "url")
    assert url.get("hide") is True

    shown = EvidentialTable(rows, link="url", show_link_column=True)
    url = next(column for column in shown.columns if column["name"] == "url")
    assert not url.get("hide")


def test_top_level_color_options_merge_into_color_options() -> None:
    table = EvidentialTable(
        [{"v": 1}],
        column_config={"v": {"viz": "color", "color_scale": "green", "color_min": 0, "color_max": 10}},
    )
    column = table.columns[0]
    assert column["color_options"]["color_scale"] == "green"
    assert column["color_options"]["min"] == 0
    assert column["color_options"]["max"] == 10
    assert "color_scale" not in column


def test_sparkline_aliases_merge_into_sparkline_options() -> None:
    table = EvidentialTable(
        [{"trend": [1, 2, 3]}],
        column_config={"trend": {"viz": "sparkline", "sparkX": "d", "sparkY": "v", "sparkColor": "#123456"}},
    )
    options = table.columns[0]["sparkline_options"]
    assert options["x"] == "d"
    assert options["y"] == "v"
    assert options["color"] == "#123456"


def test_groups_open_alias() -> None:
    closed = EvidentialTable([{"a": 1}], groups_open=False)
    assert closed.options["collapsed"] is True
    opened = EvidentialTable([{"a": 1}], groups_open=True)
    assert opened.options["collapsed"] is False


def test_logo_content_type() -> None:
    table = EvidentialTable(
        [{"domain": "github.com"}],
        columns=[{"name": "domain", "content_type": "logo"}],
    )
    assert table.columns[0]["logo"] == "domain"


def test_section_row_and_caption() -> None:
    from evidential import section_row

    table = EvidentialTable(
        [{"a": 1}, section_row("Divider"), {"a": 2}],
        columns=[{"name": "a", "type": "number"}],
        caption="Source: example",
    )
    assert table.rows[1]["render_type"] == "row_section"
    assert table.rows[1]["__label"] == "Divider"
    assert table.options["caption"] == "Source: example"


def test_blank_predicate_and_null_text() -> None:
    table = EvidentialTable(
        [{"v": 5}, {"v": 15}],
        column_config={"v": {"blank": lambda value: value < 10, "null_text": ""}},
    )
    assert table.rows[0]["v"] is None
    assert table.rows[1]["v"] == 15
    # the callable must not be serialized to the browser
    assert "blank" not in table.columns[0]
    assert table.columns[0]["null_text"] == ""


def test_null_text_option() -> None:
    table = EvidentialTable([{"a": 1}], null_text="blank")
    assert table.options["null_text"] == "blank"


def test_footnote_options_round_trip() -> None:
    table = EvidentialTable(
        [{"city": "NYC", "note": "x"}],
        column_config={"city": {"footnote": "note"}},
        footnotes=["A static note"],
    )
    assert table.columns[0]["footnote"] == "note"
    assert table.options["footnotes"] == ["A static note"]


def test_make_column_defaults() -> None:
    column = make_column("trip_distance", type="number", fmt="num1")
    assert column["name"] == "trip_distance"
    assert column["hide"] is False
    assert column["type"] == "number"


@pytest.mark.parametrize("widget", [EvidentialTable([{"a": 1}])])
def test_widget_has_static_assets(widget: EvidentialTable) -> None:
    from importlib.resources import files

    static = files("evidential").joinpath("static")
    assert static.joinpath("table.js").is_file()
    assert static.joinpath("table.css").is_file()
