import { test, beforeEach } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";

const dom = new JSDOM("<!DOCTYPE html><html><body></body></html>", { pretendToBeVisual: true });
global.window = dom.window;
global.document = dom.window.document;
global.HTMLElement = dom.window.HTMLElement;
global.Node = dom.window.Node;
global.URL = dom.window.URL;
global.Blob = dom.window.Blob;
global.ResizeObserver = class {
  observe() {}
  disconnect() {}
};
global.requestAnimationFrame = (cb) => setTimeout(() => cb(Date.now()), 0);
global.cancelAnimationFrame = (id) => clearTimeout(id);
if (!dom.window.HTMLDialogElement.prototype.showModal) {
  dom.window.HTMLDialogElement.prototype.showModal = function () { this.open = true; };
  dom.window.HTMLDialogElement.prototype.close = function () { this.open = false; this.dispatchEvent(new dom.window.Event("close")); };
}

const { EvidenceTableRenderer, holdInterval } = await import("./src/table.js");

function makeModel(rows, columns, options = {}, el) {
  const data = { rows, columns, options };
  return {
    data,
    el,
    get(key) { return data[key]; },
    on() {},
    off() {},
  };
}

const COLUMNS = [
  { name: "city", type: "string", align: "left" },
  { name: "trips", type: "number", fmt: "num0", align: "right" },
  { name: "revenue", type: "number", fmt: "usd0", viz: "bar", bar_options: {}, align: "right" },
];

const ROWS = [
  { city: "NYC", trips: 120, revenue: 4200 },
  { city: "LA", trips: 90, revenue: 3100 },
  { city: "SF", trips: 40, revenue: 1500 },
];

let el;
beforeEach(() => {
  el = document.createElement("div");
  document.body.append(el);
});

test("renders rows and formatted cells", () => {
  const renderer = new EvidenceTableRenderer(makeModel(ROWS, COLUMNS, { page_size: 10 }, el), el);
  const text = el.querySelector(".et-table").textContent;
  assert.match(text, /NYC/);
  assert.match(text, /\$4,200/);
  assert.match(text, /120/);
  const bodyRows = el.querySelectorAll("tbody tr");
  assert.equal(bodyRows.length, 3);
  renderer.destroy();
});

test("sorts by column on header click (desc -> asc -> none)", () => {
  const renderer = new EvidenceTableRenderer(makeModel(ROWS, COLUMNS, {}, el), el);
  const header = [...el.querySelectorAll("thead tr:last-child th")][1];
  header.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  let first = el.querySelector("tbody tr").textContent;
  assert.match(first, /NYC/); // 120 trips first, desc
  header.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  first = el.querySelector("tbody tr").textContent;
  assert.match(first, /SF/); // 40 trips first, asc
  renderer.destroy();
});

test("search filters rows", () => {
  const renderer = new EvidenceTableRenderer(makeModel(ROWS, COLUMNS, { search: true }, el), el);
  const input = el.querySelector(".et-search");
  input.value = "LA";
  input.dispatchEvent(new window.Event("input", { bubbles: true }));
  const bodyRows = el.querySelectorAll("tbody tr");
  assert.equal(bodyRows.length, 1);
  assert.match(bodyRows[0].textContent, /LA/);
  renderer.destroy();
});

test("pagination limits rows and pages", () => {
  const renderer = new EvidenceTableRenderer(makeModel(ROWS, COLUMNS, { page_size: 2 }, el), el);
  assert.equal(el.querySelectorAll("tbody tr").length, 2);
  const next = [...el.querySelectorAll(".et-page-controls button")][1];
  next.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  assert.equal(el.querySelectorAll("tbody tr").length, 1);
  renderer.destroy();
});

test("pagination reads as one left-aligned text run", () => {
  const renderer = new EvidenceTableRenderer(makeModel(ROWS, COLUMNS, { page_size: 2 }, el), el);
  const footer = el.querySelector(".et-footer");
  assert.equal(footer.firstElementChild.className, "et-page-controls", "pager is first");
  assert.equal(footer.lastElementChild.className, "et-table-actions", "actions are last");
  const controls = footer.querySelector(".et-page-controls");
  assert.equal(controls.querySelector(".et-page-current").textContent, "1/2");
  assert.equal(controls.querySelector(".et-page-info").textContent, "(1–2 of 3)");
  const buttons = controls.querySelectorAll("button.et-page-btn");
  assert.equal(buttons.length, 2, "the arrows are still real buttons");
  assert.equal(buttons[0].textContent, "‹");
  assert.equal(buttons[1].textContent, "›");
  renderer.destroy();
});

test("download and fullscreen live in the footer's bottom-right actions", () => {
  const renderer = new EvidenceTableRenderer(
    makeModel(ROWS, COLUMNS, { download: true, page_size: 2 }, el),
    el,
  );
  const actions = el.querySelector(".et-footer .et-table-actions");
  assert.ok(actions, "actions live in the footer");
  assert.equal(actions.querySelector(".et-download-btn").textContent, "Download");
  assert.equal(actions.querySelector(".et-expand-btn").textContent, "⛶");
  // They are gone from the toolbar, which now hides when it holds nothing.
  assert.equal(el.querySelectorAll(".et-toolbar .et-btn, .et-toolbar .et-text-btn").length, 0);
  assert.ok(el.querySelector(".et-toolbar").classList.contains("et-toolbar-empty"));
  renderer.destroy();
});

test("the fullscreen action stays available without pagination or download", () => {
  const renderer = new EvidenceTableRenderer(makeModel(ROWS, COLUMNS, {}, el), el);
  assert.equal(el.querySelectorAll(".et-page-controls").length, 0);
  assert.ok(el.querySelector(".et-footer .et-expand-btn"), "expand stays available");
  renderer.destroy();
});

test("hold repeat interval eases from 700ms to 100ms by 3s", () => {
  assert.equal(holdInterval(0), 700);
  assert.equal(holdInterval(700), 700);
  assert.equal(holdInterval(1850), 400);
  assert.equal(holdInterval(3000), 100);
  assert.equal(holdInterval(10000), 100);
});

test("holding the next button auto-repeats after a delay", (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  const rows = Array.from({ length: 6 }, (_, i) => ({ city: `C${i}`, trips: i, revenue: i * 10 }));
  const renderer = new EvidenceTableRenderer(makeModel(rows, COLUMNS, { page_size: 1 }, el), el);
  assert.equal(renderer._state.page, 0);

  const next = [...el.querySelectorAll(".et-page-controls button")][1];
  next.dispatchEvent(new window.Event("pointerdown", { bubbles: true }));
  t.mock.timers.tick(699);
  assert.equal(renderer._state.page, 0, "no repeat before the 700ms delay");
  t.mock.timers.tick(1);
  assert.equal(renderer._state.page, 1, "first repeat at 700ms");
  t.mock.timers.tick(700);
  assert.equal(renderer._state.page, 2, "next repeat after the initial interval");

  renderer._stopHold();
  t.mock.timers.tick(10000);
  assert.equal(renderer._state.page, 2, "releasing stops the repeat");
  renderer.destroy();
});

test("renders grouped subtotal rows and collapses", () => {
  const rows = [
    { country: "USA", city: "NYC", revenue: 100, render_type: "cell_data", __level: 2, __ancestors: ['"USA"'], __parent_key: '"USA"' },
    { country: "USA", city: "LA", revenue: 200, render_type: "cell_data", __level: 2, __ancestors: ['"USA"'], __parent_key: '"USA"' },
    { country: "USA", city: "", revenue: 300, render_type: "row_subtotal", __level: 1, __group_key: '"USA"', __ancestors: [], __parent_key: null },
  ];
  const columns = [
    { name: "country", type: "string", align: "left" },
    { name: "city", type: "string", align: "left" },
    { name: "revenue", type: "number", fmt: "usd0", align: "right" },
  ];
  const renderer = new EvidenceTableRenderer(
    makeModel(rows, columns, { collapsible: true, collapsed: false }, el),
    el,
  );
  assert.equal(el.querySelectorAll("tbody tr").length, 3);
  const subtotalCell = el.querySelector(".et-chevron").closest("td");
  subtotalCell.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  // Collapsing USA hides the two detail rows.
  assert.equal(el.querySelectorAll("tbody tr").length, 1);
  renderer.destroy();
});

test("fullscreen moves the widget into the dialog", () => {
  const renderer = new EvidenceTableRenderer(makeModel(ROWS, COLUMNS, {}, el), el);
  const root = el.querySelector(".et-root");
  assert.ok(el.contains(root));

  const expand = el.querySelector(".et-expand-btn");
  expand.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  assert.equal(renderer._expanded, true);
  assert.ok(el.querySelector("dialog").contains(root));

  renderer._closeExpanded();
  assert.equal(renderer._expanded, false);
  // The widget must return to the cell, not vanish into the closed dialog.
  assert.ok(el.contains(root));
  assert.ok(!el.querySelector("dialog").contains(root));
  assert.equal(root.querySelectorAll("tbody tr").length, 3);
  renderer.destroy();
});

test("leaving fullscreen restores the inline height", () => {
  const renderer = new EvidenceTableRenderer(makeModel(ROWS, COLUMNS, { page_size: 2 }, el), el);
  let natural = 120;
  // Simulate layout: the measured height is at least min-height.
  renderer.scroller.getBoundingClientRect = () => ({
    height: Math.max(natural, parseFloat(renderer.scroller.style.minHeight) || 0),
  });
  renderer.render();
  assert.equal(renderer.scroller.style.minHeight, "120px");

  // Enter fullscreen: taller viewport, larger fitted page size.
  renderer._expanded = true;
  natural = 600;
  renderer._pageSizeOverride = 20;
  el.querySelector("dialog").append(el.querySelector(".et-root"));
  renderer.render();
  assert.equal(renderer.scroller.style.minHeight, "600px");

  // Leave fullscreen: natural inline height again; must not keep 600px.
  natural = 120;
  renderer._restoreInline();
  assert.equal(renderer._pageSizeOverride, null);
  assert.equal(renderer.scroller.style.minHeight, "120px", "fullscreen height not retained");
  renderer.destroy();
});

test("fullscreen page-size override applies and resets the inline size", () => {
  const renderer = new EvidenceTableRenderer(makeModel(ROWS, COLUMNS, { page_size: 2 }, el), el);
  assert.equal(el.querySelectorAll("tbody tr").length, 2);

  renderer._pageSizeOverride = 1;
  renderer.render();
  assert.equal(renderer._effectivePageSize(), 1);
  assert.equal(el.querySelectorAll("tbody tr").length, 1);

  // Simulate being expanded, then returning inline.
  renderer._expanded = true;
  el.querySelector("dialog").append(el.querySelector(".et-root"));
  renderer._restoreInline();
  assert.equal(renderer._pageSizeOverride, null);
  assert.equal(renderer._effectivePageSize(), 2);
  assert.equal(el.querySelectorAll("tbody tr").length, 2);
  renderer.destroy();
});

test("fullscreen clears max_height so rows can expand", () => {
  const renderer = new EvidenceTableRenderer(
    makeModel(ROWS, COLUMNS, { page_size: 2, max_height: "200px" }, el),
    el,
  );
  const scroller = el.querySelector(".et-scroller");
  assert.equal(scroller.style.maxHeight, "200px");

  renderer._expanded = true;
  renderer.render();
  assert.equal(scroller.style.maxHeight, "none");

  renderer._expanded = false;
  renderer.render();
  assert.equal(scroller.style.maxHeight, "200px");
  renderer.destroy();
});

test("clicking the backdrop dismisses the fullscreen dialog", () => {
  const renderer = new EvidenceTableRenderer(makeModel(ROWS, COLUMNS, {}, el), el);
  const dialog = el.querySelector("dialog");
  const root = el.querySelector(".et-root");

  el.querySelector(".et-expand-btn").click();
  assert.equal(renderer._expanded, true);
  dialog.dispatchEvent(new window.Event("pointerdown", { bubbles: true }));
  dialog.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  assert.equal(renderer._expanded, false);
  assert.ok(el.contains(root));

  // A drag that starts inside the content and ends on the backdrop must not close.
  el.querySelector(".et-expand-btn").click();
  assert.equal(renderer._expanded, true);
  root.dispatchEvent(new window.Event("pointerdown", { bubbles: true }));
  dialog.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  assert.equal(renderer._expanded, true);

  renderer._closeExpanded();
  renderer.destroy();
});

test("row shading adds alternating data rows", () => {
  const renderer = new EvidenceTableRenderer(makeModel(ROWS, COLUMNS, { row_shading: true }, el), el);
  assert.equal(el.querySelectorAll(".et-row-shaded").length, 1);
  renderer.destroy();
});

test("row_lines: false disables body row borders", () => {
  const renderer = new EvidenceTableRenderer(makeModel(ROWS, COLUMNS, { row_lines: false }, el), el);
  assert.ok(el.querySelector(".et-root").classList.contains("et-no-row-lines"));
  renderer.destroy();
});

test("grouped columns cluster under a shared header", () => {
  const columns = [
    { name: "month", type: "string", align: "left" },
    { name: "credit_card", type: "number", column_group: "Payment type", align: "right" },
    { name: "cash", type: "number", column_group: "Payment type", align: "right" },
    { name: "total", type: "number", align: "right" },
  ];
  const rows = [{ month: "Jan", credit_card: 1, cash: 2, total: 3 }];
  const renderer = new EvidenceTableRenderer(makeModel(rows, columns, {}, el), el);
  const headers = [...el.querySelectorAll("thead tr:last-child th")].map((th) => th.textContent.trim());
  assert.deepEqual(headers, ["Month", "Credit Card", "Cash", "Total"]);
  const groupCells = [...el.querySelectorAll(".et-th-group")].map((th) => ({
    text: th.textContent,
    span: th.colSpan,
  }));
  assert.deepEqual(groupCells, [
    { text: "", span: 1 },
    { text: "Payment type", span: 2 },
    { text: "", span: 1 },
  ]);
  renderer.destroy();
});

test("loading overlay only appears for slow updates, and fades in", (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  const renderer = new EvidenceTableRenderer(makeModel(ROWS, COLUMNS, {}, el), el);
  const root = el.querySelector(".et-root");
  const overlay = el.querySelector(".et-loading-overlay");
  assert.ok(overlay, "overlay element exists");
  assert.equal(root.classList.contains("et-loading"), false);

  // Fast update: finishes before the show delay, so nothing flashes.
  renderer.setLoading(true);
  t.mock.timers.tick(100);
  renderer.setLoading(false);
  t.mock.timers.tick(1000);
  assert.equal(root.classList.contains("et-loading"), false, "fast update does not flash");

  // Slow update: stays loading past the show delay, so the overlay fades in.
  renderer.setLoading(true);
  t.mock.timers.tick(200);
  assert.equal(root.classList.contains("et-loading"), true, "slow update shows processing");

  renderer.setLoading(false);
  t.mock.timers.tick(700);
  assert.equal(root.classList.contains("et-loading"), false, "new data revealed");
  renderer.destroy();
});

test("baseline height prevents the table shrinking when rows decrease", () => {
  const renderer = new EvidenceTableRenderer(makeModel(ROWS, COLUMNS, {}, el), el);
  let height = 300;
  renderer.scroller.getBoundingClientRect = () => ({ height });
  renderer.render();
  assert.equal(renderer.scroller.style.minHeight, "300px");

  height = 120; // e.g. the live filter returns fewer rows
  renderer.render();
  assert.equal(renderer.scroller.style.minHeight, "300px");
  renderer.destroy();
});

test("renders line, area and bar sparklines from point arrays", () => {
  const columns = [
    { name: "category", type: "string" },
    { name: "s1", type: "array", viz: "sparkline", sparkline_options: { x: "date", y: "sales", type: "line" } },
    { name: "s2", type: "array", viz: "sparkline", sparkline_options: { x: "date", y: "sales", type: "area", color: "#53768a" } },
    { name: "s3", type: "array", viz: "sparkline", sparkline_options: { x: "date", y: "sales", type: "bar" } },
  ];
  const series = [
    { date: "2024-01-01", sales: 10 },
    { date: "2024-02-01", sales: 20 },
    { date: "2024-03-01", sales: 15 },
  ];
  const rows = [{ category: "A", s1: series, s2: series, s3: series }];
  const renderer = new EvidenceTableRenderer(makeModel(rows, columns, {}, el), el);
  assert.equal(el.querySelectorAll("svg.et-sparkline").length, 3);
  assert.equal(el.querySelectorAll("svg.et-sparkline polyline").length, 2); // line + area outline
  assert.equal(el.querySelectorAll("svg.et-sparkline polygon").length, 1); // area fill
  assert.equal(el.querySelectorAll("svg.et-sparkline rect").length, 3); // bars
  renderer.destroy();
});

test("sparklines accept plain numbers and [x, y] pairs", () => {
  const columns = [{ name: "s", type: "array", viz: "sparkline" }];
  const renderer = new EvidenceTableRenderer(
    makeModel([{ s: [1, 2, 3] }, { s: [["a", 4], ["b", 6]] }], columns, {}, el),
    el,
  );
  const sparklines = el.querySelectorAll("svg.et-sparkline");
  assert.equal(sparklines.length, 2);
  assert.equal(sparklines[0].querySelectorAll("circle").length, 3);
  assert.equal(sparklines[1].querySelectorAll("circle").length, 2);
  renderer.destroy();
});

test("row numbers, compact density and empty message", () => {
  const numbered = new EvidenceTableRenderer(
    makeModel(ROWS, COLUMNS, { row_numbers: true }, el),
    el,
  );
  assert.equal(el.querySelectorAll(".et-row-num").length, 4); // header + 3 rows
  assert.equal(el.querySelector("tbody .et-row-num").textContent, "1");
  numbered.destroy();

  const compact = new EvidenceTableRenderer(makeModel(ROWS, COLUMNS, { compact: true }, el), el);
  assert.ok(el.querySelector(".et-root").classList.contains("et-compact"));
  compact.destroy();

  const empty = new EvidenceTableRenderer(
    makeModel([], COLUMNS, { empty_message: "Nothing here" }, el),
    el,
  );
  assert.equal(el.querySelector(".et-empty").textContent, "Nothing here");
  empty.destroy();
});

test("default_sort sorts on first render", () => {
  const renderer = new EvidenceTableRenderer(
    makeModel(ROWS, COLUMNS, { default_sort: { column: "trips", direction: "asc" } }, el),
    el,
  );
  assert.match(el.querySelector("tbody tr").textContent, /SF/);
  assert.ok(el.querySelector(".et-th-sorted"));
  renderer.destroy();
});

test("row_conditional_colors tints the whole row", () => {
  const columns = [{ name: "city", type: "string" }, { name: "tint", type: "string", hide: true }];
  const rows = [{ city: "NYC", tint: "#ff0000" }];
  const renderer = new EvidenceTableRenderer(
    makeModel(rows, columns, { row_conditional_colors: "tint" }, el),
    el,
  );
  const cell = el.querySelector("tbody .et-td");
  assert.equal(cell.style.backgroundColor, "rgb(255, 0, 0)");
  renderer.destroy();
});

test("fmt_column applies a per-row format code", () => {
  const columns = [
    { name: "value", type: "number", fmt_column: "fmt" },
    { name: "fmt", type: "string" },
  ];
  const rows = [
    { value: 0.1234, fmt: "pct1" },
    { value: 1234, fmt: "usd0" },
  ];
  const renderer = new EvidenceTableRenderer(makeModel(rows, columns, {}, el), el);
  const cells = [...el.querySelectorAll("tbody tr")].map(
    (tr) => tr.querySelector(".et-cell-value").textContent,
  );
  assert.equal(cells[0], "12.3%");
  assert.equal(cells[1], "$1,234");
  renderer.destroy();
});

test("delta puts the indicator after the value, with a dash when neutral", () => {
  const columns = [
    { name: "up", type: "number", fmt: "pct1", viz: "delta", delta_options: { chip: true } },
    { name: "down", type: "number", fmt: "pct1", viz: "delta" },
    {
      name: "flat",
      type: "number",
      fmt: "pct1",
      viz: "delta",
      delta_options: { neutral_range: "-0.1:0.1" },
    },
    { name: "cost", type: "number", fmt: "pct1", viz: "delta", delta_options: { down_is_good: true } },
    { name: "bare", type: "number", fmt: "pct1", viz: "delta", delta_options: { show_value: false } },
    { name: "boom", type: "number", fmt: "pct1", viz: "delta" },
  ];
  const rows = [{ up: 0.12, down: -0.04, flat: 0.03, cost: 0.05, bare: 0.12, boom: 3.0746 }];
  const renderer = new EvidenceTableRenderer(makeModel(rows, columns, {}, el), el);
  const cells = [...el.querySelectorAll(".et-delta")];
  const text = cells.map((node) => node.textContent.trim());
  assert.equal(text[0], "12.0% ▲");
  assert.equal(text[1], "4.0% ▼");
  assert.equal(text[2], "3.0% –"); // neutral -> dash
  assert.equal(text[3], "5.0% ▲");
  assert.equal(text[4], "▲"); // show_value: false
  assert.equal(text[5], "307.5% ▲"); // >100% still a percentage
  assert.equal(cells[0].querySelector(".et-delta-indicator").textContent, "▲");
  assert.equal(cells[2].querySelector(".et-delta-indicator").textContent, "–");
  assert.ok(cells[0].classList.contains("et-delta-good"));
  assert.ok(cells[1].classList.contains("et-delta-bad"));
  assert.ok(cells[2].classList.contains("et-delta-neutral"));
  assert.ok(cells[3].classList.contains("et-delta-bad")); // down_is_good flips it
  assert.ok(el.querySelector(".et-delta-chip"));
  renderer.destroy();
});

test("a missing delta renders the neutral dash, like a value in range", () => {
  const columns = [{ name: "change", type: "number", fmt: "pct1", viz: "delta" }];
  const rows = [{ change: null }];
  const renderer = new EvidenceTableRenderer(makeModel(rows, columns, {}, el), el);
  const cell = el.querySelector(".et-delta");
  assert.ok(cell, "a null delta still renders a delta");
  assert.ok(cell.classList.contains("et-delta-neutral"));
  assert.equal(cell.textContent.trim(), "–");
  assert.equal(cell.querySelector(".et-delta-indicator").textContent, "–");
  assert.equal(el.querySelector(".et-null"), null); // not the generic null cell
  renderer.destroy();
});

test("a column can sort by another column's values", () => {
  const columns = [
    { name: "name", type: "string" },
    { name: "score", type: "number", hide: true }, // in the data, not displayed
    { name: "trend", type: "number", sort_by: "score" },
  ];
  const rows = [
    { name: "A", score: 3, trend: 10 },
    { name: "B", score: 1, trend: 30 },
    { name: "C", score: 2, trend: 20 },
  ];
  const renderer = new EvidenceTableRenderer(makeModel(rows, columns, {}, el), el);
  const header = [...el.querySelectorAll(".et-th")].find((n) => n.textContent.includes("Trend"));
  header.click(); // first click = descending
  const order = [...el.querySelectorAll("tbody tr")].map((tr) => tr.querySelector("td").textContent.trim());
  assert.deepEqual(order, ["A", "C", "B"]); // by score, not by trend
  renderer.destroy();
});

test("column info renders a header icon with an immediate tooltip", () => {
  const columns = [{ name: "city", type: "string", info: "A helpful hint" }];
  const renderer = new EvidenceTableRenderer(makeModel([{ city: "NYC" }], columns, {}, el), el);
  const icon = el.querySelector(".et-th-info");
  assert.ok(icon);
  assert.equal(icon.getAttribute("aria-label"), "A helpful hint");
  assert.equal(icon.getAttribute("title"), null); // no delayed native tooltip

  icon.dispatchEvent(new dom.window.Event("mouseenter"));
  const tip = document.querySelector(".et-tooltip");
  assert.ok(tip, "tooltip appears on hover");
  assert.equal(tip.textContent, "A helpful hint");

  icon.dispatchEvent(new dom.window.Event("mouseleave"));
  assert.equal(document.querySelector(".et-tooltip"), null);
  renderer.destroy();
});

test("page_size 'all' shows every row without pagination", () => {
  const rows = Array.from({ length: 25 }, (_, i) => ({ city: `C${i}`, trips: i, revenue: i * 10 }));
  const renderer = new EvidenceTableRenderer(makeModel(rows, COLUMNS, { page_size: "all" }, el), el);
  assert.equal(el.querySelectorAll("tbody tr").length, 25);
  assert.equal(el.querySelectorAll(".et-page-controls").length, 0);
  renderer.destroy();
});

test("column statistics render under the header and before the data", () => {
  const columns = [
    { name: "city", type: "string" },
    { name: "trips", type: "number", fmt: "num0" },
  ];
  const rows = [
    { city: "NYC", trips: 120 },
    { city: "LA", trips: 90 },
    { city: "SF", trips: null },
  ];
  const renderer = new EvidenceTableRenderer(makeModel(rows, columns, { column_stats: true }, el), el);
  const first = el.querySelector("tbody tr");
  assert.ok(first.classList.contains("et-stats-row"), "stats row is the first body row");
  const cells = first.querySelectorAll(".et-stats-cell");
  assert.equal(cells.length, 2);
  assert.match(cells[0].textContent, /\[STRING\]/);
  assert.match(cells[0].textContent, /distinct: 3/);
  assert.match(cells[0].textContent, /null: 0/);
  assert.match(cells[1].textContent, /\[NUMBER\]/);
  assert.match(cells[1].textContent, /min: 90/);
  assert.match(cells[1].textContent, /max: 120/);
  assert.match(cells[1].textContent, /avg: 105/);
  assert.match(cells[1].textContent, /null: 1/);
  renderer.destroy();
});

test("column statistics are off unless requested", () => {
  const renderer = new EvidenceTableRenderer(makeModel(ROWS, COLUMNS, {}, el), el);
  assert.equal(el.querySelector(".et-stats-row"), null);
  renderer.destroy();
});

test("logo columns render a logo.dev image", () => {
  const columns = [
    { name: "company", type: "string", logo: "domain" },
    { name: "domain", type: "string", hide: true },
  ];
  const rows = [{ company: "GitHub", domain: "github.com" }];
  const renderer = new EvidenceTableRenderer(makeModel(rows, columns, {}, el), el);
  const img = el.querySelector(".et-cell-logo");
  assert.ok(img);
  assert.match(img.getAttribute("src"), /img\.logo\.dev\/github\.com/);
  renderer.destroy();
});

test("total_fmt and subtotal_fmt override row formats", () => {
  const columns = [{ name: "amount", type: "number", fmt: "num0", total_fmt: "usd0", subtotal_fmt: "usd2" }];
  const rows = [
    { amount: 1000, render_type: "cell_data" },
    { amount: 1000, render_type: "row_subtotal" },
    { amount: 2000, render_type: "row_total" },
  ];
  const renderer = new EvidenceTableRenderer(makeModel(rows, columns, {}, el), el);
  const cells = [...el.querySelectorAll("tbody tr .et-cell-value")].map((c) => c.textContent);
  assert.equal(cells[0], "1,000");
  assert.equal(cells[1], "$1,000.00");
  assert.equal(cells[2], "$2,000");
  renderer.destroy();
});

test("section groups merge the dimension cell with rowspan", () => {
  const columns = [
    { name: "country", type: "string", align: "left" },
    { name: "city", type: "string", align: "left" },
    { name: "revenue", type: "number", fmt: "usd0", align: "right" },
  ];
  const rows = [
    { country: "USA", city: "", revenue: 350, render_type: "row_subtotal", __level: 1, __group_key: '"USA"', __ancestors: [] },
    { country: "USA", city: "NYC", revenue: 100, render_type: "cell_data", __level: 2, __ancestors: ['"USA"'], __parent_key: '"USA"' },
    { country: "USA", city: "LA", revenue: 250, render_type: "cell_data", __level: 2, __ancestors: ['"USA"'], __parent_key: '"USA"' },
    { country: "Canada", city: "", revenue: 200, render_type: "row_subtotal", __level: 1, __group_key: '"Canada"', __ancestors: [] },
    { country: "Canada", city: "Toronto", revenue: 200, render_type: "cell_data", __level: 2, __ancestors: ['"Canada"'], __parent_key: '"Canada"' },
  ];
  const renderer = new EvidenceTableRenderer(
    makeModel(rows, columns, { group_type: "section", subtotal_position: "top" }, el),
    el,
  );
  const bodyRows = el.querySelectorAll("tbody tr");
  const usaCells = bodyRows[0].querySelectorAll("td");
  assert.equal(usaCells.length, 2); // city cell is covered by the rowspan
  assert.equal(usaCells[0].getAttribute("rowspan"), "3");
  const detailCells = bodyRows[1].querySelectorAll("td");
  assert.equal(detailCells.length, 2); // country cell is covered
  assert.equal(detailCells[0].textContent, "NYC");
  renderer.destroy();
});

test("section rows span all columns", () => {
  const columns = [
    { name: "label", type: "string" },
    { name: "a", type: "number" },
    { name: "b", type: "number" },
  ];
  const rows = [
    { label: "Metric", a: 1, b: 2 },
    { render_type: "row_section", __label: "Section header" },
    { label: "Metric 2", a: 3, b: 4 },
  ];
  const renderer = new EvidenceTableRenderer(makeModel(rows, columns, {}, el), el);
  const section = el.querySelector(".et-row-section td");
  assert.ok(section);
  assert.equal(section.getAttribute("colspan"), "3");
  assert.equal(section.textContent, "Section header");
  renderer.destroy();
});

test("caption renders below the table", () => {
  const renderer = new EvidenceTableRenderer(
    makeModel(ROWS, COLUMNS, { caption: "Source: example" }, el),
    el,
  );
  assert.equal(el.querySelector(".et-caption").textContent, "Source: example");
  renderer.destroy();
});

test("blank_below/above and null_text control blank cells", () => {
  const columns = [
    { name: "v", type: "number", fmt: "num0", blank_below: 10 },
    { name: "n", type: "number", fmt: "num0", null_text: "" },
  ];
  const rows = [
    { v: 5, n: null },
    { v: 15, n: 3 },
  ];
  const renderer = new EvidenceTableRenderer(makeModel(rows, columns, {}, el), el);
  const bodyRows = el.querySelectorAll("tbody tr");
  assert.equal(bodyRows[0].querySelectorAll("td")[0].querySelector(".et-null").textContent, "–");
  assert.equal(bodyRows[0].querySelectorAll("td")[1].querySelector(".et-null").textContent, "");
  assert.equal(bodyRows[1].querySelectorAll("td")[0].textContent, "15");
  renderer.destroy();
});

test("data-driven footnotes collect notes with row numbers", () => {
  const columns = [
    { name: "city", type: "string", footnote: "note" },
    { name: "trips", type: "number" },
    { name: "note", type: "string", hide: true },
  ];
  const rows = [
    { city: "NYC", trips: 1, note: "Custom processors" },
    { city: "LA", trips: 2, note: null },
    { city: "SF", trips: 3, note: "Custom processors" },
    { city: "CHI", trips: 4, note: "Smart-phone / tablet" },
  ];
  const renderer = new EvidenceTableRenderer(makeModel(rows, columns, {}, el), el);
  const items = el.querySelectorAll(".et-footnotes .et-footnote-item");
  assert.equal(items.length, 2);
  assert.match(items[0].textContent, /Custom processors/);
  assert.match(items[0].textContent, /rows 1, 3/);
  assert.match(items[1].textContent, /rows 4/);
  renderer.destroy();
});

test("nested column groups build multiple header rows", () => {
  const columns = [
    { name: "city", type: "string" },
    { name: "sales21", type: "number", column_group: ["Sales", "2021"] },
    { name: "orders21", type: "number", column_group: ["Sales", "2021"] },
    { name: "sales22", type: "number", column_group: ["Sales", "2022"] },
  ];
  const rows = [{ city: "NYC", sales21: 1, orders21: 2, sales22: 3 }];
  const renderer = new EvidenceTableRenderer(makeModel(rows, columns, {}, el), el);
  const groupRows = el.querySelectorAll("thead .et-header-groups");
  assert.equal(groupRows.length, 2);
  const level0 = [...groupRows[0].querySelectorAll("th")];
  assert.equal(level0[0].textContent, "");
  assert.equal(level0[1].textContent, "Sales");
  assert.equal(level0[1].getAttribute("colspan"), "3");
  const level1 = [...groupRows[1].querySelectorAll("th")];
  assert.equal(level1[1].textContent, "2021");
  assert.equal(level1[1].getAttribute("colspan"), "2");
  renderer.destroy();
});

test("array column groups cluster at their first occurrence", () => {
  const columns = [
    { name: "a", type: "number", column_group: ["G", "1"] },
    { name: "x", type: "number" },
    { name: "b", type: "number", column_group: ["G", "1"] },
  ];
  const rows = [{ a: 1, x: 2, b: 3 }];
  const renderer = new EvidenceTableRenderer(makeModel(rows, columns, {}, el), el);
  const leaf = [...el.querySelectorAll("thead tr:last-child .et-th-title")].map((n) => n.textContent);
  assert.deepEqual(leaf, ["A", "B", "X"]);
  renderer.destroy();
});

test("location rules apply per-cell style and format", () => {
  const columns = [
    { name: "city", type: "string" },
    { name: "trips", type: "number", fmt: "id" },
  ];
  const rows = [
    { city: "NYC", trips: 12000, __row_id: 0 },
    { city: "LA", trips: 8000, __row_id: 1 },
  ];
  const rules = [{ columns: ["trips"], rows: [0], style: { color: "#b91c1c" }, fmt: "num0" }];
  const renderer = new EvidenceTableRenderer(makeModel(rows, columns, { rules }, el), el);
  const firstTrips = el.querySelectorAll("tbody tr")[0].querySelectorAll("td")[1];
  assert.equal(firstTrips.style.color, "rgb(185, 28, 28)");
  assert.equal(firstTrips.textContent, "12,000");
  renderer.destroy();
});

test("inline markdown renders in the title", () => {
  const renderer = new EvidenceTableRenderer(
    makeModel(ROWS, COLUMNS, { title: "**Bold** title" }, el),
    el,
  );
  const strong = el.querySelector(".et-title strong");
  assert.ok(strong);
  assert.equal(strong.textContent, "Bold");
  renderer.destroy();
});

test("stub head label is used for the stub column", () => {
  const columns = [
    { name: "city", type: "string" },
    { name: "trips", type: "number" },
  ];
  const renderer = new EvidenceTableRenderer(
    makeModel([{ city: "NYC", trips: 1 }], columns, { stub: "city", stub_head: "Place" }, el),
    el,
  );
  assert.equal(el.querySelector(".et-stub-head").textContent.trim(), "Place");
  assert.ok(el.querySelector("tbody .et-stub"));
  renderer.destroy();
});

test("substitution rules replace displayed values", () => {
  const columns = [{ name: "v", type: "number", fmt: "num0" }];
  const rows = [
    { v: 0, __row_id: 0 },
    { v: 5, __row_id: 1 },
    { v: 0.001, __row_id: 2 },
  ];
  const rules = [
    { type: "substitute", columns: ["v"], rows: null, kind: "zero", text: "—" },
    { type: "substitute", columns: ["v"], rows: null, kind: "small", threshold: 0.01, text: "small" },
  ];
  const renderer = new EvidenceTableRenderer(makeModel(rows, columns, { rules }, el), el);
  const cells = [...el.querySelectorAll("tbody .et-cell-value")].map((cell) => cell.textContent);
  assert.deepEqual(cells, ["—", "5", "small"]);
  renderer.destroy();
});

test("column templates merge rendered values", () => {
  const columns = [
    { name: "low", type: "number", fmt: "num0" },
    { name: "high", type: "number", fmt: "num0" },
    { name: "range", type: "string", template: "{low}–{high}", template_fmt: { low: "num0", high: "num0" } },
  ];
  const rows = [{ low: 10, high: 20 }];
  const renderer = new EvidenceTableRenderer(makeModel(rows, columns, {}, el), el);
  const cells = [...el.querySelectorAll("tbody .et-cell-value")].map((cell) => cell.textContent);
  assert.equal(cells[2], "10–20");
  renderer.destroy();
});

test("markdown columns render inline markdown", () => {
  const columns = [{ name: "label", type: "string", markdown: true }];
  const rows = [{ label: "**Hi** there" }];
  const renderer = new EvidenceTableRenderer(makeModel(rows, columns, {}, el), el);
  assert.ok(el.querySelector("tbody .et-cell-value strong"));
  renderer.destroy();
});

test("footnote_marks letters uses letter marks", () => {
  const columns = [
    { name: "city", type: "string", footnote: "note" },
    { name: "note", type: "string", hide: true },
  ];
  const rows = [
    { city: "A", note: "first" },
    { city: "B", note: "second" },
  ];
  const renderer = new EvidenceTableRenderer(
    makeModel(rows, columns, { footnote_marks: "letters" }, el),
    el,
  );
  const marks = [...el.querySelectorAll("tbody .et-footnote-mark")].map((mark) => mark.textContent);
  assert.deepEqual(marks, ["a", "b"]);
  renderer.destroy();
});

test("align_decimals pads numeric columns to a common precision", () => {
  const columns = [{ name: "v", type: "number", fmt: "num", align: "right" }];
  const rows = [{ v: 1.5 }, { v: 12.25 }, { v: 3 }];
  const renderer = new EvidenceTableRenderer(
    makeModel(rows, columns, { align_decimals: true }, el),
    el,
  );
  const cells = [...el.querySelectorAll("tbody .et-cell-value")].map((cell) => cell.textContent);
  assert.deepEqual(cells, ["1.50", "12.25", "3.00"]);
  renderer.destroy();
});

test("stretch=false keeps the table content-sized", () => {
  const renderer = new EvidenceTableRenderer(
    makeModel(ROWS, COLUMNS, { stretch: false }, el),
    el,
  );
  assert.ok(el.querySelector(".et-root").classList.contains("et-stretch-off"));
  renderer.destroy();
});

test("row_shading supports group sizes (3,3)", () => {
  const rows = Array.from({ length: 6 }, (_, i) => ({ city: `C${i}`, trips: i, revenue: i * 10 }));
  const renderer = new EvidenceTableRenderer(makeModel(rows, COLUMNS, { row_shading: 3 }, el), el);
  const shaded = [...el.querySelectorAll("tbody tr")].map((tr) =>
    tr.classList.contains("et-row-shaded"),
  );
  assert.deepEqual(shaded, [false, false, false, true, true, true]);
  renderer.destroy();
});

test("row_shading pair sets shaded/unshaded counts", () => {
  const rows = Array.from({ length: 4 }, (_, i) => ({ city: `C${i}`, trips: i, revenue: i * 10 }));
  const renderer = new EvidenceTableRenderer(makeModel(rows, COLUMNS, { row_shading: [1, 3] }, el), el);
  const shaded = [...el.querySelectorAll("tbody tr")].map((tr) =>
    tr.classList.contains("et-row-shaded"),
  );
  assert.deepEqual(shaded, [false, false, false, true]);
  renderer.destroy();
});

test("rotated headers: vertical and oblique", () => {
  const columns = [
    { name: "a", type: "number" },
    { name: "b", type: "number" },
  ];
  const rows = [{ a: 1, b: 2 }];

  const vertical = new EvidenceTableRenderer(
    makeModel(rows, columns, { rotate_titles: "vertical" }, el),
    el,
  );
  assert.equal(el.querySelectorAll(".et-th-vertical").length, 2);
  vertical.destroy();

  const oblique = new EvidenceTableRenderer(
    makeModel(rows, columns, { rotate_titles: -45 }, el),
    el,
  );
  const obliqueTh = el.querySelector(".et-th-oblique");
  assert.ok(obliqueTh);
  assert.equal(obliqueTh.style.getPropertyValue("--et-th-angle"), "-45deg");
  oblique.destroy();
});

test("figure_style sets font-variant-numeric", () => {
  const columns = [{ name: "v", type: "number", fmt: "num0", figure_style: "oldstyle" }];
  const renderer = new EvidenceTableRenderer(makeModel([{ v: 1234 }], columns, {}, el), el);
  const td = el.querySelector("tbody .et-td");
  assert.equal(td.style.fontVariantNumeric, "oldstyle-nums tabular-nums");
  renderer.destroy();
});

test("per-column font sets font-family", () => {
  const columns = [{ name: "v", type: "number", font: "'Hoefler Text', serif" }];
  const renderer = new EvidenceTableRenderer(makeModel([{ v: 1234 }], columns, {}, el), el);
  const td = el.querySelector("tbody .et-td");
  assert.match(td.style.fontFamily, /Hoefler/);
  renderer.destroy();
});

test("figure_style default uses the font's own figures", () => {
  const columns = [{ name: "v", type: "number", figure_style: "default" }];
  const renderer = new EvidenceTableRenderer(makeModel([{ v: 1234 }], columns, {}, el), el);
  assert.equal(el.querySelector("tbody .et-td").style.fontVariantNumeric, "normal");
  renderer.destroy();
});

test("no viz badge is added to headers", () => {
  const columns = [{ name: "v", type: "number", viz: "bar", bar_options: {} }];
  const renderer = new EvidenceTableRenderer(makeModel([{ v: 1 }], columns, {}, el), el);
  assert.equal(el.querySelectorAll(".et-viz-badge").length, 0);
  renderer.destroy();
});

test("theme.background drives the opaque expanded surface", () => {
  const renderer = new EvidenceTableRenderer(
    makeModel(ROWS, COLUMNS, { theme: { background: "#123456" } }, el),
    el,
  );
  const root = el.querySelector(".et-root");
  assert.equal(root.style.getPropertyValue("--et-surface"), "#123456");
  renderer.destroy();
});
