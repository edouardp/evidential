"""Browser checks for the plain, bevelled HTML time machine."""

import pytest

from evidential import EvidentialTable
from scripts.api_screenshots import _server

pytestmark = pytest.mark.browser


def test_netscape_has_classic_borders_blue_headers_and_raw_text(page):
    table = EvidentialTable(
        [
            {"Person": "Starflower", "Food": "Stir fried tofu", "Amount": 1234.5},
            {"Person": "Miko", "Food": "Vegetable rice soup", "Amount": -2},
        ]
    )
    page.set_content(str(table.netscape_navigator_96()))
    assert page.locator("table.netscape").count() == 1
    assert page.locator("tbody td").all_text_contents() == [
        "Starflower",
        "Stir fried tofu",
        "1234.5",
        "Miko",
        "Vegetable rice soup",
        "-2",
    ]
    styles = page.locator("table").evaluate("""table => {
        const style = getComputedStyle(table);
        const header = getComputedStyle(table.querySelector('th'));
        const cell = getComputedStyle(table.querySelector('td'));
        return {
            collapse: style.borderCollapse, spacing: style.borderSpacing,
            border: style.borderTopWidth, top: style.borderTopColor, bottom: style.borderBottomColor,
            headerBackground: header.backgroundColor, headerSize: header.fontSize, headerAlign: header.textAlign,
            cellBackground: cell.backgroundColor, cellSize: cell.fontSize, cellHeight: cell.lineHeight,
            cellBorder: cell.borderTopStyle, cellWrap: cell.whiteSpace,
        };
    }""")
    assert styles == {
        "collapse": "separate",
        "spacing": "1px",
        "border": "10px",
        "top": "rgb(176, 176, 176)",
        "bottom": "rgb(80, 80, 80)",
        "headerBackground": "rgb(153, 204, 255)",
        "headerSize": "17px",
        "headerAlign": "center",
        "cellBackground": "rgb(255, 255, 255)",
        "cellSize": "14px",
        "cellHeight": "14px",
        "cellBorder": "inset",
        "cellWrap": "nowrap",
    }
    assert page.locator("script, canvas, svg, input").count() == 0


def test_netscape_renders_directly_as_a_marimo_cell_output(page, tmp_path):
    notebook = tmp_path / "retro.py"
    notebook.write_text("""import marimo
app = marimo.App()

@app.cell
def _():
    from evidential import EvidentialTable
    return (EvidentialTable,)

@app.cell
def retro(EvidentialTable):
    EvidentialTable([
        {"Person": "Starflower", "Food": "Stir fried tofu"},
        {"Person": "Miko", "Food": "Vegetable rice soup"},
    ]).netscape_navigator_96()
    return

if __name__ == "__main__":
    app.run()
""")
    with _server(notebook) as url:
        page.goto(url, wait_until="networkidle")
        table = page.locator('[data-cell-name="retro"] table.netscape')
        table.wait_for(state="visible", timeout=60_000)
        assert table.locator("th").all_text_contents() == ["Person", "Food"]
        assert table.locator("td").all_text_contents() == [
            "Starflower",
            "Stir fried tofu",
            "Miko",
            "Vegetable rice soup",
        ]
        assert table.evaluate("el => getComputedStyle(el).borderTopWidth") == "10px"
        assert table.locator("th").first.evaluate("el => getComputedStyle(el).backgroundColor") == "rgb(153, 204, 255)"
        page.screenshot(path=str(tmp_path / "netscape-marimo.png"))
