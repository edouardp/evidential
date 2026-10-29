"""Real scrolling/search and kernel-backed hierarchical filtering."""

import pytest
from playwright.sync_api import expect

from scripts.api_screenshots import ROOT, _server

pytestmark = pytest.mark.browser


def test_wheel_horizontal_navigation_search_and_keyboard(page, live_server):
    page.goto(live_server)
    page.evaluate(
        """async () => {
          const css = document.createElement('link');
          css.rel = 'stylesheet'; css.href = '/src/evidential/static/dimension-grid.css';
          document.head.append(css);
          const {default: widget} = await import('/src/evidential/static/dimension-grid.js');
          const state = {
            options: {format:'num0', height:280, dimension_width:220, color:'#93b4ef', multiple:true},
            selected: {},
            facets: Array.from({length:20}, (_, i) => ({name:`dimension_${i}`, items:
              Array.from({length:230}, (_, j) => ({value:`Category ${j}`, metric:230-j}))}))
          };
          const listeners = new Map();
          window.model = {
            get: name => state[name],
            set(name, value) {state[name]=value; for (const fn of listeners.get(`change:${name}`)||[]) fn();},
            on(name, fn) {if (!listeners.has(name)) listeners.set(name,new Set()); listeners.get(name).add(fn);},
            off(name, fn) {listeners.get(name)?.delete(fn);}, save_changes() {}
          };
          document.body.replaceChildren();
          const el = document.createElement('main'); el.style.width='740px'; document.body.append(el);
          widget.render({model:window.model, el});
        }"""
    )
    dimension = page.locator(".edg-dimension").first
    assert dimension.locator(".edg-status").evaluate("el => getComputedStyle(el).textAlign") == "center"
    listing = dimension.locator(".edg-list")
    fifth = listing.locator(".edg-row").nth(4)
    before = fifth.bounding_box()
    fifth.click()
    selected = listing.locator('.edg-row[aria-pressed="true"]')
    expect(selected).to_contain_text("Category 4")
    assert selected.bounding_box()["y"] == before["y"]
    assert selected.evaluate("el => getComputedStyle(el).fontWeight") == "700"
    marker = selected.evaluate("""el => {
      const style = getComputedStyle(el, '::before');
      return {width: style.width, height: style.height, color: style.backgroundColor};
    }""")
    assert marker == {"width": "6px", "height": "20px", "color": "rgb(139, 30, 45)"}
    assert listing.evaluate("el => getComputedStyle(el).scrollbarWidth") == "thin"
    selected.click()
    listing.hover()
    page.mouse.wheel(0, 1100)
    page.wait_for_function("document.querySelector('.edg-list').scrollTop > 500")
    assert dimension.locator(".edg-row").count() < 30
    assert "Category 0," not in dimension.locator(".edg-row").first.get_attribute("aria-label")
    page.get_by_role("button", name="Next dimensions", exact=True).click()
    page.wait_for_function("document.querySelector('.edg-track').scrollLeft > 100")
    page.get_by_role("button", name="Previous dimensions", exact=True).click()
    page.wait_for_function("document.querySelector('.edg-track').scrollLeft < 1")
    dimension.get_by_role("button", name="Search Dimension 0", exact=True).click()
    search = dimension.get_by_role("searchbox")
    search.fill("Category 228")
    expect(dimension.locator(".edg-row")).to_have_count(1)
    dimension.locator(".edg-row").click()
    expect(search).to_be_hidden()
    expect(dimension.locator(".edg-search-toggle")).to_have_class("edg-search-toggle edg-filtered")
    expect(dimension.locator('.edg-list .edg-row[aria-pressed="true"]')).to_have_count(1)
    dimension.locator(".edg-search-toggle").click()
    dimension.locator(".edg-search-toggle").click()
    listing.focus()
    page.keyboard.press("End")
    expect(dimension.locator(".edg-list .edg-row").last).to_be_focused()
    page.keyboard.press("Enter")
    assert len(page.evaluate("window.model.get('selected').dimension_0")) == 2
    page.emulate_media(color_scheme="dark")
    assert page.locator(".edg-root").evaluate("el => getComputedStyle(el).backgroundColor") == "rgb(255, 255, 255)"
    page.screenshot(path="/private/tmp/evidential-dimensions-white.png")
    page.set_viewport_size({"width": 420, "height": 700})
    page.locator("main").evaluate("el => el.style.width = '100%'")
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")


def test_needful_things_demo_cross_filters_with_a_live_kernel(page):
    with _server(ROOT / "notebooks" / "56_dimension_grid.py") as url:
        page.goto(url)
        orders = page.locator('[data-cell-name="orders_grid"] .edg-root')
        orders.wait_for(timeout=60_000)
        assert orders.locator(".edg-title").evaluate("el => getComputedStyle(el).fontWeight") == "700"
        expect(orders.locator(".edg-dimension")).to_have_count(4)
        monthly = page.locator('[data-cell-name="monthly_table"] .et-table')
        expect(monthly.locator("tbody tr").first).to_contain_text("Jan-19", timeout=30_000)
        grid_font = orders.evaluate("el => [getComputedStyle(el).fontSize, getComputedStyle(el).fontFamily]")
        table_font = monthly.evaluate("el => [getComputedStyle(el).fontSize, getComputedStyle(el).fontFamily]")
        assert grid_font == table_font
        unfiltered_month = monthly.locator("tbody tr").first.inner_text()
        orders.screenshot(path="/private/tmp/evidential-dimensions-orders.png")
        category = orders.get_by_role("region", name="Category", exact=True)
        category.locator(".edg-row").first.click()
        expect(category.locator('.edg-row[aria-pressed="true"]')).to_have_count(1)
        item = orders.get_by_role("region", name="Item", exact=True)
        expect(item.locator(".edg-status")).to_have_text("3 available")
        # A source-linked monthly result changes after filtering (sum rather than a copied fixture).
        expect(monthly.locator("tbody tr").first).not_to_have_text(unfiltered_month)
        category.locator(".edg-list .edg-row").nth(1).click()
        expect(category.locator('.edg-row[aria-pressed="true"]')).to_have_count(2)
        expect(item.locator(".edg-status")).to_have_text("6 available")
        orders.screenshot(path="/private/tmp/evidential-dimensions-selected.png")
