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

  const expand = el.querySelector(".et-icon-btn");
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

  el.querySelector(".et-icon-btn").click();
  assert.equal(renderer._expanded, true);
  dialog.dispatchEvent(new window.Event("pointerdown", { bubbles: true }));
  dialog.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  assert.equal(renderer._expanded, false);
  assert.ok(el.contains(root));

  // A drag that starts inside the content and ends on the backdrop must not close.
  el.querySelector(".et-icon-btn").click();
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

test("theme.background drives the opaque expanded surface", () => {
  const renderer = new EvidenceTableRenderer(
    makeModel(ROWS, COLUMNS, { theme: { background: "#123456" } }, el),
    el,
  );
  const root = el.querySelector(".et-root");
  assert.equal(root.style.getPropertyValue("--et-surface"), "#123456");
  renderer.destroy();
});
