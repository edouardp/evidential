"""Touch inspection coexists with row selection and renderer disposal."""

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser


def test_touch_inspection_retains_selection_and_cleans_up(browser, live_server):
    context = browser.new_context(has_touch=True, viewport={"width": 700, "height": 600})
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    try:
        page.goto(f"{live_server}/frontend/preview.html", wait_until="networkidle")
        page.evaluate("""async () => {
            const {default: widget} = await import('/src/evidential/static/table.js');
            document.body.replaceChildren();
            const el = document.createElement('div');
            document.body.append(el);
            const handlers = new Map();
            const data = {rows: [{name: 'North', value: 1234.56}],
                columns: [{name: 'name'}, {name: 'value', fmt: 'compact',
                    encodings: [{kind: 'point', source: 'value'}]}],
                options: {select: 'name', search: false, page_size: 0}};
            window.tooltipModel = {get: key => data[key],
                set(key, value) { data[key] = value; handlers.get('change:' + key)?.(); },
                save_changes() {}, on(name, fn) { handlers.set(name, fn); }, off(name) { handlers.delete(name); }};
            window.disposeTooltips = widget.render({el, model: window.tooltipModel});
        }""")
        point = page.locator(".et-mark-point")
        point.tap()
        expect(page.locator(".et-tooltip")).to_be_visible()
        expect(page.locator(".et-tooltip-value")).to_have_text("1,234.56")
        assert page.evaluate("tooltipModel.get('selected')") == "North"
        assert page.locator(".et-row-selected").count() == 1
        # A later model update clears the popup rather than keeping an old row.
        page.evaluate("tooltipModel.set('selected', null)")
        expect(page.locator(".et-tooltip")).to_be_hidden()
        page.locator(".et-mark-point").tap()
        expect(page.locator(".et-tooltip")).to_be_visible()
        page.evaluate("disposeTooltips()")
        expect(page.locator(".et-tooltip")).to_have_count(0)
        page.mouse.move(20, 20)
        assert errors == []
    finally:
        context.close()
