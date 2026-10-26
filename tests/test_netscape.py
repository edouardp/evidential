"""The undocumented trip back to 1996 uses raw records and ordinary HTML."""

from xml.etree import ElementTree

import duckdb
import marimo as mo

from evidential import EvidentialTable, LiveEvidentialTable, col, rows
from evidential.rules import cells_body, text_transform


def _table(view):
    return ElementTree.fromstring(str(view).split("</style>", 1)[1])


def test_netscape_uses_raw_fields_and_values_in_source_order():
    table = EvidentialTable(
        [{"person": "Starflower", "amount": 1234.5, "hidden": False, "missing": None}],
        columns=[
            col.currency("amount", title="Pretty amount").blank(lambda row: True),
            col.text("person"),
            col.boolean("hidden").hide(),
        ],
        rules=[text_transform(cells_body("person"), str.upper)],
        title="Not in the time machine",
        row_layout=rows.group_by("person").section().summary().grand_summary(),
        page_size=1,
    )
    view = table.netscape_navigator_96()
    markup = str(view)
    element = _table(view)
    assert [cell.text for cell in element.findall("./thead/tr/th")] == ["person", "amount", "hidden", "missing"]
    assert [[cell.text for cell in row] for row in element.findall("./tbody/tr")] == [
        ["Starflower", "1234.5", "False", "None"]
    ]
    assert "Pretty amount" not in markup and "Not in the time machine" not in markup
    assert "table.netscape" in markup and "border: 10px solid" in markup and "#99ccff" in markup
    assert view._repr_html_() == markup
    assert mo.as_html(view)._repr_html_() == markup


def test_netscape_escapes_headers_and_values_as_literal_text():
    table = EvidentialTable([{'<name & "label">': '<script>alert("1996")</script> & friends'}])
    view = table.netscape_navigator_96()
    assert "<script>" not in str(view)
    assert _table(view).find("./thead/tr/th").text == '<name & "label">'
    assert _table(view).find("./tbody/tr/td").text == '<script>alert("1996")</script> & friends'


def test_netscape_keeps_later_fields_nested_values_and_all_rows():
    data = [{"name": "A", "series": [1, 2]}, {"name": "B", "extra": {"n": 3}}]
    table = EvidentialTable(data, page_size=1, default_sort={"column": "name", "direction": "desc"})
    element = _table(table.netscape_navigator_96())
    assert [cell.text for cell in element.findall("./thead/tr/th")] == ["name", "series", "extra"]
    assert [[cell.text for cell in row] for row in element.findall("./tbody/tr")] == [
        ["A", "[1, 2]", None],
        ["B", None, "{'n': 3}"],
    ]
    assert table.raw == data


def test_netscape_handles_empty_data_and_returns_a_static_snapshot():
    table = EvidentialTable()
    empty = table.netscape_navigator_96()
    assert _table(empty).findall(".//tr") == []
    table.set_data([{"Person": "Miko", "Food": "Vegetable rice soup"}])
    view = table.netscape_navigator_96()
    table.set_data([{"Person": "Starflower", "Food": "Stir fried tofu"}])
    assert "Miko" in str(view) and "Starflower" not in str(view)
    assert "Starflower" in str(table.netscape_navigator_96())
    assert _table(empty).findall(".//tr") == []


def test_live_netscape_uses_latest_successful_result_without_running_sql():
    with duckdb.connect() as connection:
        connection.execute("CREATE SEQUENCE visits")
        table = LiveEvidentialTable(connection, "SELECT nextval('visits') AS visit", auto_run=False)
        assert _table(table.netscape_navigator_96()).findall(".//tr") == []
        table.run()
        first = table.netscape_navigator_96()
        assert _table(first).find("./tbody/tr/td").text == "1"
        assert _table(table.netscape_navigator_96()).find("./tbody/tr/td").text == "1"
        table.run()
        assert _table(table.netscape_navigator_96()).find("./tbody/tr/td").text == "2"
        assert _table(first).find("./tbody/tr/td").text == "1"
