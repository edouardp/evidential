"""Host prose styles, including CSS copied into marimo's outer shadow root."""

import re

import pytest
from playwright.sync_api import expect
from test_spec_conformance import mount

from evidential import EvidentialTable, col, label

pytestmark = pytest.mark.browser

# The blog's table rules, plus intentionally aggressive host selectors.
HOST_CSS = """
table {font-size:.9em; border-collapse:collapse; border-top:2px solid red;
       border-bottom:2px solid red; margin:2em; width:70%;}
table tr {cursor:pointer;}
table tr:nth-child(6n+4), table tr:nth-child(6n+5), table tr:nth-child(6n+6) {background:orange;}
tbody tr:hover {background:magenta;}
thead {border-bottom:1px solid red;}
table th {text-align:center !important; font-size:1.11em; padding:6px 13px;}
table td {padding:6px 13px; box-shadow:-1px 0 0 red;}
article table td {border:9px solid lime !important;}
button, input {background:orange !important; color:purple !important; font-size:40px !important;}
svg {display:none !important;}
"""


@pytest.mark.parametrize("scheme", ["light", "dark"])
def test_host_and_copied_marimo_css_cannot_change_widget_presentation(page, live_server, scheme):
    table = EvidentialTable(
        [{"name": f"Item {i}", "score": i + 1, "trend": [1, 3, 2, 6]} for i in range(12)],
        columns=[
            col.text("name", info="Item name"),
            col.bar("score", label=label.auto_position("outside end")).scale(domain=(0, 12), axis=True),
            col.sparkline("trend", type="area"),
        ],
        color_scheme="auto",
        page_size=5,
        search=True,
        freeze_columns=1,
        row_shading=True,
        theme_source="host",
    )
    mount(page, live_server, [("Host CSS", table, [])])
    root = page.locator(".et-root")
    page.locator("html").evaluate("(el, scheme) => el.dataset.theme = scheme", scheme)
    expect(root).to_have_attribute("data-color-scheme", scheme)
    selectors = ["table", "thead", "th", "td", "tbody tr:nth-child(4)", "button", "input", "svg"]
    snapshot = """async (root, selectors) => {
        // Theme changes replace the table. Frozen offsets and label fitting run
        // on the following frame, including a possible ResizeObserver pass.
        await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
        return selectors.map(selector => {
            const s=getComputedStyle(root.querySelector(selector));
            return Object.fromEntries(
                ['fontSize','fontFamily','padding','borderTop','borderBottom','boxShadow','backgroundColor',
                 'textAlign','display','color','margin','width','cursor'].map(k=>[k,s[k]]));
        });
    }"""
    expect(root.locator("th").first).to_have_class(re.compile("et-frozen"))
    before = root.evaluate(snapshot, selectors)
    # Reproduce marimo's existing shadow root with host CSS copied into it.
    page.locator("#case-0").evaluate(
        """(host, css) => {
      const outer = document.createElement('marimo-island'); host.before(outer);
      const shadow = outer.attachShadow({mode:'open'});
      const style=document.createElement('style'); style.textContent=css;
      const wrapper=document.createElement('article'); wrapper.className='light';
      shadow.append(style,wrapper); wrapper.append(host);
    }""",
        HOST_CSS,
    )
    page.add_style_tag(content=HOST_CSS)
    expect(root).to_have_attribute("data-color-scheme", scheme)
    assert root.evaluate(snapshot, selectors) == before
    assert root.locator("table").evaluate("el => el.getRootNode() !== el.getRootNode().host.getRootNode()")
    root.locator('th[data-column="score"]').click()
    expect(root.locator("tbody tr").first).to_contain_text("Item 11")
    root.get_by_role("searchbox").fill("Item 1")
    expect(root.locator("tbody tr")).to_have_count(3)
    root.get_by_role("searchbox").fill("")
    root.get_by_role("button", name="Expand table", exact=True).click()
    expect(page.locator("dialog")).to_be_visible()
    root.get_by_role("searchbox").focus()
    # Fullscreen fitting can still increase the visible capacity after focus.
    # Arrow keys in the search field must preserve the page's record offset,
    # independently of how many trailing rows fit after the next layout pass.
    first_record = root.locator("tbody td:first-child").first.inner_text()
    page.keyboard.press("ArrowRight")
    expect(root.get_by_role("searchbox")).to_be_focused()
    expect(root.locator("tbody td:first-child").first).to_have_text(first_record)
    page.keyboard.press("Escape")
    expect(page.locator("dialog")).not_to_be_visible()
    root.screenshot(path=f"/tmp/evidential-host-css-{scheme}.png")
    # Theme attribute changes still cross both shadow boundaries.
    other = "dark" if scheme == "light" else "light"
    page.locator("html").evaluate("(el, scheme) => el.dataset.theme = scheme", other)
    expect(root).to_have_attribute("data-color-scheme", other)
