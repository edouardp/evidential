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

const { EvidentialTableRenderer, render, fontSizeValue } = await import("./src/table.js");

test("numeric color and chip scales use inferred ranges", () => {
  for (const viz of ["color", "chip"]) {
    const renderer = new EvidentialTableRenderer(
      makeModel([{ x: 1 }, { x: 10 }], [{ name: "x", type: "number", viz, color_options: { color_scale: "green" } }], {}, el), el,
    );
    const targets = [...el.querySelectorAll(viz === "chip" ? ".et-chip" : "tbody td")];
    assert.ok(targets[0].style.backgroundColor);
    assert.notEqual(targets[0].style.backgroundColor, targets[1].style.backgroundColor);
    renderer.destroy();
  }
});

test("theme options update and removing overrides restores inherited tokens", () => {
  const model = makeModel([{ x: 1 }], [{ name: "x" }], { theme: { background: "red" } }, el);
  const renderer = new EvidentialTableRenderer(model, el);
  model.data.options = { theme: { background: "blue" } };
  renderer.render();
  assert.equal(renderer.root.style.getPropertyValue("--et-bg"), "blue");
  assert.equal(renderer.dialog.style.getPropertyValue("--et-bg"), "blue");
  model.data.options = {};
  renderer.render();
  assert.equal(renderer.root.style.getPropertyValue("--et-bg"), "");
  assert.equal(renderer.dialog.style.getPropertyValue("--et-bg"), "");
  renderer.destroy();
});

test("styles and footnotes compose with nulls, substitutions and templates", () => {
  const columns = [{ name: "empty" }, { name: "zero" }, { name: "merged", template: "{other}" }];
  const rows = [{ empty: null, zero: 0, other: "hello", note: "A note", __row_id: 0 }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {
    footnote_column: "note",
    rules: [
      { columns: "*", rows: [0], style: { "background-color": "red" } },
      { type: "substitute", columns: ["zero"], kind: "zero", text: "none" },
    ],
  }, el), el);
  const cells = [...el.querySelectorAll("tbody td")];
  assert.ok(cells.every((cell) => cell.style.backgroundColor === "red"));
  assert.ok(cells.every((cell) => cell.querySelector(".et-footnote-mark")));
  assert.match(cells[1].textContent, /none/);
  assert.match(cells[2].textContent, /hello/);
  renderer.destroy();
});

test("sorting and selection support keyboard activation", () => {
  const model = makeModel([{ x: 1 }, { x: 2 }], [{ name: "x", type: "number" }], { select: "x" }, el);
  const renderer = new EvidentialTableRenderer(model, el);
  const header = el.querySelector("th");
  assert.equal(header.tabIndex, 0);
  header.dispatchEvent(new window.KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
  assert.match(el.querySelector("tbody tr").textContent, /2/);
  const row = el.querySelector("tbody tr");
  assert.equal(row.tabIndex, 0);
  row.dispatchEvent(new window.KeyboardEvent("keydown", { key: " ", bubbles: true }));
  assert.equal(model.data.selected, 2);
  renderer.render();
  assert.equal(el.querySelector("tbody tr").getAttribute("aria-selected"), "true");
  renderer.destroy();
});

test("group chevrons are native buttons with expansion state", () => {
  const rows = [
    { x: "A", render_type: "row_subtotal", __level: 1, __group_key: "A", __ancestors: [] },
    { x: "A", y: "B", render_type: "cell_data", __level: 2, __ancestors: ["A"] },
  ];
  const renderer = new EvidentialTableRenderer(
    makeModel(rows, [{ name: "x" }, { name: "y" }], { collapsible: true, collapsed: false }, el), el,
  );
  const button = el.querySelector("button.et-chevron");
  assert.ok(button);
  assert.equal(button.getAttribute("aria-expanded"), "true");
  button.click();
  assert.equal(el.querySelectorAll("tbody tr").length, 1);
  assert.equal(el.querySelector("button.et-chevron").getAttribute("aria-expanded"), "false");
  renderer.destroy();
});

test("keyboard selection restores focus after a model-driven render", (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  const model = makeModel([{ x: 1 }], [{ name: "x" }], { select: "x" }, el);
  const renderer = new EvidentialTableRenderer(model, el);
  model.set = (key, value) => { model.data[key] = value; renderer.render(); };
  const row = el.querySelector("tbody tr");
  row.focus();
  row.dispatchEvent(new window.KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
  t.mock.timers.tick(1);
  assert.equal(document.activeElement, el.querySelector("tbody tr"));
  renderer.destroy();
});

test("page navigation reuses dataset summaries and invalidates changed inputs", () => {
  let reads = 0;
  const rows = Array.from({ length: 1000 }, (_, index) => ({ get value() { reads++; return index; } }));
  const model = makeModel(rows, [{ name: "value", type: "number", fmt: "num" }],
    { page_size: 2, column_stats: true }, el);
  const renderer = new EvidentialTableRenderer(model, el);
  reads = 0;
  renderer._gotoPage(1);
  assert.ok(reads < 10, `navigation scanned ${reads} values`);
  reads = 0;
  model.data.options = { ...model.data.options, align_decimals: true };
  renderer.render();
  assert.ok(reads >= rows.length, "changed options recompute dataset summaries");
  model.data.rows = [{ value: 3000 }, { value: 4000 }];
  renderer.render();
  assert.match(el.querySelector(".et-stats").textContent, /4k/);
  model.data.columns = [{ name: "value", type: "number", fmt: "usd0" }];
  renderer.render();
  assert.match(el.querySelector("tbody .et-cell-value").textContent, /\$/);
  renderer.destroy();
});

test("decimal alignment handles datasets beyond JavaScript argument limits", () => {
  const rows = Array.from({ length: 200000 }, (_, index) => ({ value: index + 0.125 }));
  const renderer = new EvidentialTableRenderer(makeModel(rows,
    [{ name: "value", type: "number", fmt: "num" }], { page_size: 2, align_decimals: true }, el), el);
  assert.equal(el.querySelectorAll("tbody tr").length, 2);
  assert.match(el.querySelector("tbody tr").textContent, /0\.125/);
  renderer.destroy();
});

test("comm updates invalidate caches even when array identity is unchanged", async () => {
  const model = makeModel([{value: 1}], [{name: "value", type: "number"}], {column_stats: true}, el);
  const events = new Map();
  model.on = (event, callback) => events.set(event, callback);
  model.off = (event) => events.delete(event);
  const dispose = render({model, el});
  model.data.rows[0].value = 99;
  events.get("change:rows")();
  await Promise.resolve();
  assert.match(el.querySelector(".et-stats").textContent, /99/);
  dispose();
  assert.equal(events.size, 0);
});

test("batched comm changes render once and pending work stops on disposal", async () => {
  const model = makeModel([{value: 1}], [{name: "value"}], {}, el);
  const events = new Map();
  model.on = (event, callback) => events.set(event, callback);
  model.off = (event) => events.delete(event);
  const dispose = render({model, el});
  const initial = Number(el.dataset.renderCount);
  model.data.rows = [{value: 2}];
  model.data.columns = [{name: "value", type: "number", fmt: "num0"}];
  model.data.options = {column_stats: true};
  for (const trait of ["rows", "columns", "options"]) events.get(`change:${trait}`)();
  await Promise.resolve();
  assert.equal(Number(el.dataset.renderCount), initial + 1);
  assert.match(el.querySelector(".et-stats").textContent, /2/);
  events.get("change:rows")();
  dispose();
  await Promise.resolve();
  assert.equal(Number(el.dataset.renderCount), initial + 1);
});

test("display annotations have independent cells, style, numbering and selection", () => {
  const model = makeModel([{city: "A", value: 10}, {city: "B", value: 20}],
    [{name: "city"}, {name: "value", type: "number", fmt: "num1", encodings: [{kind: "bar", source: "value"}]}],
    {row_numbers: true, row_shading: true, select: "city", page_size: 1}, el);
  model.data.row_layout = {version: 1, groups: [{id: "all", members: [0, 1], depth: 0, children: [],
    section: {label: "Group", cells: {city: {value: "2 products"}, value: {value: "Approved"}},
      style: {font_weight: "normal"}, rule: "below"},
    summary: {label: "Subtotal", cells: {value: {operation: "sum", source: "value"}}, position: "bottom"}}]};
  const renderer = new EvidentialTableRenderer(model, el);
  const heading = el.querySelector(".et-display-section");
  assert.match(heading.textContent, /Group2 productsApproved/);
  assert.equal(heading.querySelectorAll(".et-marks").length, 0);
  assert.ok(heading.classList.contains("et-display-rule-below"));
  assert.equal(heading.querySelector(".et-row-num").textContent, "");
  assert.equal(heading.querySelectorAll("td")[1].style.fontWeight, "normal");
  heading.click();
  assert.equal(model.data.selected, null);
  assert.deepEqual([...el.querySelectorAll("tbody .et-row-num")].map(cell => cell.textContent), ["", "1"]);
  renderer._gotoPage(1);
  assert.match(el.querySelector(".et-row-continuation").textContent, /Group \(cont\.\)/);
  assert.deepEqual([...el.querySelectorAll("tbody .et-row-num")].map(cell => cell.textContent), ["2", ""]);
  assert.equal(el.querySelector(".et-display-summary .et-display-value").textContent, "30.0");
  renderer.destroy();
});

test("row layout comm changes rerender and dispose their listener", async () => {
  const model = makeModel([{value: 1}], [{name: "value"}], {}, el);
  const events = new Map();
  model.on = (event, callback) => events.set(event, callback);
  model.off = event => events.delete(event);
  const dispose = render({model, el});
  model.data.row_layout = {version: 1, groups: [], grand_summary: {label: "Total", cells: {value: {operation: "sum", source: "value"}}}};
  events.get("change:row_layout")();
  await Promise.resolve();
  assert.equal(el.querySelectorAll(".et-display-grand_summary").length, 1);
  dispose();
  assert.equal(events.size, 0);
});

test("nested layout indentation reflects each displayed group level", () => {
  const model = makeModel([{city: "A", value: 10}], [{name: "city"}, {name: "value"}], {section_indent: 1}, el);
  model.data.row_layout = {version: 1, groups: [{id: "root", members: [0], depth: 0,
    section: {label: "Root"}, children: [{id: "child", members: [0], depth: 1, children: [], section: {label: "Child"}}]}]};
  const renderer = new EvidentialTableRenderer(model, el);
  const displayed = [...el.querySelectorAll("tbody tr")];
  assert.equal(displayed[1].querySelector("td").style.paddingLeft, "calc(1.25rem)");
  assert.equal(displayed[2].querySelector("td").style.paddingLeft, "calc(2.25rem)");
  renderer.destroy();
});

function makeModel(rows, columns, options = {}, el) {
  const data = { rows, columns, options, selected: null };
  const calls = [];
  return {
    data,
    calls,
    el,
    get(key) { return data[key]; },
    set(key, value) { data[key] = value; calls.push(["set", key, value]); },
    save_changes() { calls.push(["save_changes"]); },
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
  const renderer = new EvidentialTableRenderer(makeModel(ROWS, COLUMNS, { page_size: 10 }, el), el);
  const text = el.querySelector(".et-table").textContent;
  assert.match(text, /NYC/);
  assert.match(text, /\$4,200/);
  assert.match(text, /120/);
  const bodyRows = el.querySelectorAll("tbody tr");
  assert.equal(bodyRows.length, 3);
  renderer.destroy();
});

test("sorts by column on header click (desc -> asc -> none)", () => {
  const renderer = new EvidentialTableRenderer(makeModel(ROWS, COLUMNS, {}, el), el);
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
  const renderer = new EvidentialTableRenderer(makeModel(ROWS, COLUMNS, { search: true }, el), el);
  const input = el.querySelector(".et-search");
  input.value = "LA";
  input.dispatchEvent(new window.Event("input", { bubbles: true }));
  const bodyRows = el.querySelectorAll("tbody tr");
  assert.equal(bodyRows.length, 1);
  assert.match(bodyRows[0].textContent, /LA/);
  renderer.destroy();
});

test("pagination limits rows and pages", () => {
  const renderer = new EvidentialTableRenderer(makeModel(ROWS, COLUMNS, { page_size: 2 }, el), el);
  assert.equal(el.querySelectorAll("tbody tr").length, 2);
  const next = [...el.querySelectorAll(".et-page-controls button")][1];
  next.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  assert.equal(el.querySelectorAll("tbody tr").length, 1);
  renderer.destroy();
});

test("pagination reads as one left-aligned text run", () => {
  const renderer = new EvidentialTableRenderer(makeModel(ROWS, COLUMNS, { page_size: 2 }, el), el);
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

test("the actions float only when content below would otherwise be pushed down", () => {
  const rows = [
    { site: "A", value: 1, note: "first" },
    { site: "B", value: 2, note: "second" },
    { site: "C", value: 3, note: "first" },
  ];
  // All combinations of pager / caption / footnote. The actions float only with
  // no pager *and* something below it; otherwise the footer stays in flow.
  for (const pageSize of ["all", 2]) {
    for (const caption of [false, true]) {
      for (const footnote of [false, true]) {
        const site = { name: "site", type: "string", align: "left" };
        if (footnote) site.footnote = "note";
        const options = { page_size: pageSize };
        if (caption) options.caption = "Source: test.";
        const renderer = new EvidentialTableRenderer(
          makeModel(rows.map((row) => ({ ...row })), [site, { name: "value", type: "number", fmt: "num0" }], options, el),
          el,
        );
        const floats = pageSize === "all" && (caption || footnote);
        assert.equal(
          el.querySelector(".et-root").classList.contains("et-float-actions"),
          floats,
          `page_size=${pageSize} caption=${caption} footnote=${footnote}`,
        );
        renderer.destroy();
      }
    }
  }
});

test("download and fullscreen live in the footer's bottom-right actions", () => {
  const renderer = new EvidentialTableRenderer(
    makeModel(ROWS, COLUMNS, { download: true, page_size: 2 }, el),
    el,
  );
  const actions = el.querySelector(".et-footer .et-table-actions");
  assert.ok(actions, "actions live in the footer");
  assert.equal(actions.querySelector(".et-download-btn").textContent, "⤓ Download");
  assert.equal(actions.querySelector(".et-expand-btn").textContent, "⛶ Expand");
  // They are gone from the toolbar, which now hides when it holds nothing.
  assert.equal(el.querySelectorAll(".et-toolbar .et-btn, .et-toolbar .et-text-btn").length, 0);
  assert.ok(el.querySelector(".et-toolbar").classList.contains("et-toolbar-empty"));
  renderer.destroy();
});

test("the fullscreen action stays available without pagination or download", () => {
  const renderer = new EvidentialTableRenderer(makeModel(ROWS, COLUMNS, {}, el), el);
  assert.equal(el.querySelectorAll(".et-page-controls").length, 0);
  assert.ok(el.querySelector(".et-footer .et-expand-btn"), "expand stays available");
  renderer.destroy();
});

test("holding the next button auto-repeats after a delay", (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  const rows = Array.from({ length: 6 }, (_, i) => ({ city: `C${i}`, trips: i, revenue: i * 10 }));
  const renderer = new EvidentialTableRenderer(makeModel(rows, COLUMNS, { page_size: 1 }, el), el);
  assert.equal(renderer._state.page, 0);

  const next = [...el.querySelectorAll(".et-page-controls button")][1];
  next.dispatchEvent(new window.Event("pointerdown", { bubbles: true }));
  t.mock.timers.tick(699);
  assert.equal(renderer._state.page, 0, "no repeat before the 700ms delay");
  t.mock.timers.tick(1);
  assert.equal(renderer._state.page, 1, "first repeat at 700ms");
  t.mock.timers.tick(700);
  assert.equal(renderer._state.page, 2, "next repeat after the initial interval");

  window.dispatchEvent(new window.Event("pointerup"));
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
  const renderer = new EvidentialTableRenderer(
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
  const renderer = new EvidentialTableRenderer(makeModel(ROWS, COLUMNS, {}, el), el);
  const root = el.querySelector(".et-root");
  assert.ok(el.contains(root));

  const expand = el.querySelector(".et-expand-btn");
  expand.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  assert.equal(renderer._viewport.expanded, true);
  assert.ok(el.querySelector("dialog").contains(root));

  el.querySelector(".et-close-btn").click();
  assert.equal(renderer._viewport.expanded, false);
  // The widget must return to the cell, not vanish into the closed dialog.
  assert.ok(el.contains(root));
  assert.ok(!el.querySelector("dialog").contains(root));
  assert.equal(root.querySelectorAll("tbody tr").length, 3);
  renderer.destroy();
});

test("expanded mode offers a close icon in the corner", () => {
  const renderer = new EvidentialTableRenderer(makeModel(ROWS, COLUMNS, {}, el), el);
  const close = el.querySelector(".et-close-btn");
  assert.ok(close, "close button exists");
  assert.equal(close.textContent, "✕");
  assert.equal(close.getAttribute("aria-label"), "Close expanded table");
  assert.equal(el.querySelector(".et-root").classList.contains("et-expanded"), false);
  const expand = el.querySelector(".et-expand-btn");
  expand.click();
  assert.ok(el.querySelector(".et-root").classList.contains("et-expanded"));
  // The footer toggle stays, marked with the × that means "close it".
  assert.equal(expand.textContent, "× Expand");
  close.click();
  assert.equal(renderer._viewport.expanded, false);
  renderer.destroy();
});

test("leaving fullscreen restores the inline height", () => {
  const renderer = new EvidentialTableRenderer(makeModel(ROWS, COLUMNS, { page_size: 2 }, el), el);
  let natural = 120;
  // Simulate layout: the measured height is at least min-height.
  renderer.scroller.getBoundingClientRect = () => ({
    height: Math.max(natural, parseFloat(renderer.scroller.style.minHeight) || 0),
  });
  renderer.render();
  assert.equal(renderer.scroller.style.minHeight, "120px");

  // Enter fullscreen: taller viewport, larger fitted page size.
  renderer._viewport.expanded = true;
  natural = 600;
  renderer._pageSizeOverride = 20;
  el.querySelector("dialog").append(el.querySelector(".et-root"));
  renderer.render();
  assert.equal(renderer.scroller.style.minHeight, "600px");

  // Leave fullscreen: natural inline height again; must not keep 600px.
  natural = 120;
  renderer._viewport.restore();
  assert.equal(renderer._pageSizeOverride, null);
  assert.equal(renderer.scroller.style.minHeight, "120px", "fullscreen height not retained");
  renderer.destroy();
});

test("fullscreen page-size override applies and resets the inline size", () => {
  const renderer = new EvidentialTableRenderer(makeModel(ROWS, COLUMNS, { page_size: 2 }, el), el);
  assert.equal(el.querySelectorAll("tbody tr").length, 2);

  renderer._pageSizeOverride = 1;
  renderer.render();
  assert.equal(renderer._effectivePageSize(), 1);
  assert.equal(el.querySelectorAll("tbody tr").length, 1);

  // Simulate being expanded, then returning inline.
  renderer._viewport.expanded = true;
  el.querySelector("dialog").append(el.querySelector(".et-root"));
  renderer._viewport.restore();
  assert.equal(renderer._pageSizeOverride, null);
  assert.equal(renderer._effectivePageSize(), 2);
  assert.equal(el.querySelectorAll("tbody tr").length, 2);
  renderer.destroy();
});

test("fullscreen clears max_height so rows can expand", () => {
  const renderer = new EvidentialTableRenderer(
    makeModel(ROWS, COLUMNS, { page_size: 2, max_height: "200px" }, el),
    el,
  );
  const scroller = el.querySelector(".et-scroller");
  assert.equal(scroller.style.maxHeight, "200px");

  renderer._viewport.expanded = true;
  renderer.render();
  assert.equal(scroller.style.maxHeight, "none");

  renderer._viewport.expanded = false;
  renderer.render();
  assert.equal(scroller.style.maxHeight, "200px");
  renderer.destroy();
});

test("clicking the backdrop dismisses the fullscreen dialog", () => {
  const renderer = new EvidentialTableRenderer(makeModel(ROWS, COLUMNS, {}, el), el);
  const dialog = el.querySelector("dialog");
  const root = el.querySelector(".et-root");

  el.querySelector(".et-expand-btn").click();
  assert.equal(renderer._viewport.expanded, true);
  dialog.dispatchEvent(new window.Event("pointerdown", { bubbles: true }));
  dialog.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  assert.equal(renderer._viewport.expanded, false);
  assert.ok(el.contains(root));

  // A drag that starts inside the content and ends on the backdrop must not close.
  el.querySelector(".et-expand-btn").click();
  assert.equal(renderer._viewport.expanded, true);
  root.dispatchEvent(new window.Event("pointerdown", { bubbles: true }));
  dialog.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  assert.equal(renderer._viewport.expanded, true);

  el.querySelector(".et-close-btn").click();
  renderer.destroy();
});

test("row shading adds alternating data rows", () => {
  const renderer = new EvidentialTableRenderer(makeModel(ROWS, COLUMNS, { row_shading: true }, el), el);
  assert.equal(el.querySelectorAll(".et-row-shaded").length, 1);
  renderer.destroy();
});

test("row_lines: false disables body row borders", () => {
  const renderer = new EvidentialTableRenderer(makeModel(ROWS, COLUMNS, { row_lines: false }, el), el);
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
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
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
  const renderer = new EvidentialTableRenderer(makeModel(ROWS, COLUMNS, {}, el), el);
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
  const renderer = new EvidentialTableRenderer(makeModel(ROWS, COLUMNS, {}, el), el);
  let height = 300;
  renderer.scroller.getBoundingClientRect = () => ({ height });
  renderer.render();
  assert.equal(renderer.scroller.style.minHeight, "300px");

  height = 120; // e.g. the live filter returns fewer rows
  renderer.render();
  assert.equal(renderer.scroller.style.minHeight, "300px");
  renderer.destroy();
});

test("expanding or collapsing a group resets the height baseline", () => {
  const columns = [
    { name: "city", type: "string", align: "left" },
    { name: "trips", type: "number" },
  ];
  const rows = [
    { city: "A", trips: 1, render_type: "row_subtotal", __level: 1, __group_key: '"A"', __ancestors: [] },
    { city: "x", trips: 1, render_type: "cell_data", __level: 2, __ancestors: ['"A"'], __parent_key: '"A"' },
  ];
  const renderer = new EvidentialTableRenderer(
    makeModel(rows, columns, { collapsible: true, collapsed: false }, el),
    el,
  );
  let height = 300;
  renderer.scroller.getBoundingClientRect = () => ({ height });
  renderer.render();
  assert.equal(renderer.scroller.style.minHeight, "300px");
  height = 40; // collapsing the group leaves the subtotal row only
  renderer._toggleGroup('"A"');
  assert.equal(renderer.scroller.style.minHeight, "40px");
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
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
  assert.equal(el.querySelectorAll("svg.et-sparkline").length, 3);
  assert.equal(el.querySelectorAll("svg.et-sparkline polyline").length, 2); // line + area outline
  assert.equal(el.querySelectorAll("svg.et-sparkline polygon").length, 1); // area fill
  assert.equal(el.querySelectorAll("svg.et-sparkline rect").length, 3); // bars
  renderer.destroy();
});

test("sparklines accept plain numbers and [x, y] pairs", () => {
  const columns = [{ name: "s", type: "array", viz: "sparkline" }];
  const renderer = new EvidentialTableRenderer(
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
  const numbered = new EvidentialTableRenderer(
    makeModel(ROWS, COLUMNS, { row_numbers: true }, el),
    el,
  );
  assert.equal(el.querySelectorAll(".et-row-num").length, 4); // header + 3 rows
  assert.equal(el.querySelector("tbody .et-row-num").textContent, "1");
  numbered.destroy();

  const compact = new EvidentialTableRenderer(makeModel(ROWS, COLUMNS, { compact: true }, el), el);
  assert.ok(el.querySelector(".et-root").classList.contains("et-compact"));
  compact.destroy();

  const empty = new EvidentialTableRenderer(
    makeModel([], COLUMNS, { empty_message: "Nothing here", page_size: 4 }, el),
    el,
  );
  // The headers stay and the body is blank rows under the message overlay.
  assert.equal(el.querySelectorAll("thead th").length, COLUMNS.length);
  assert.equal(el.querySelectorAll(".et-row-placeholder").length, 4);
  assert.equal(el.querySelector(".et-empty-body").dataset.emptyMessage, "Nothing here");
  empty.destroy();
});

test("empty_rows controls how many blank rows an empty table shows", () => {
  const renderer = new EvidentialTableRenderer(makeModel([], COLUMNS, { empty_rows: 6 }, el), el);
  assert.equal(el.querySelectorAll(".et-row-placeholder").length, 6);
  renderer.destroy();
});

test("an empty table with no columns falls back to a plain message", () => {
  const renderer = new EvidentialTableRenderer(
    makeModel([], [], { empty_message: "Nothing here" }, el),
    el,
  );
  assert.equal(el.querySelector(".et-empty").textContent, "Nothing here");
  assert.equal(el.querySelectorAll(".et-row-placeholder").length, 0);
  renderer.destroy();
});

test("border=False drops the outer frame", () => {
  const renderer = new EvidentialTableRenderer(makeModel(ROWS, COLUMNS, { border: false }, el), el);
  assert.ok(el.querySelector(".et-root").classList.contains("et-no-border"));
  renderer.destroy();
  const framed = new EvidentialTableRenderer(makeModel(ROWS, COLUMNS, {}, el), el);
  assert.ok(!el.querySelector(".et-root").classList.contains("et-no-border"));
  framed.destroy();
});

test("default_sort sorts on first render", () => {
  const renderer = new EvidentialTableRenderer(
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
  const renderer = new EvidentialTableRenderer(
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
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
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
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
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
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
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
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
  const header = [...el.querySelectorAll(".et-th")].find((n) => n.textContent.includes("Trend"));
  header.click(); // first click = descending
  const order = [...el.querySelectorAll("tbody tr")].map((tr) => tr.querySelector("td").textContent.trim());
  assert.deepEqual(order, ["A", "C", "B"]); // by score, not by trend
  renderer.destroy();
});

test("a newline in a column title forces a line break", () => {
  const columns = [{ name: "revenue", type: "number", title: "Revenue\n(USD thousands)" }];
  const renderer = new EvidentialTableRenderer(makeModel([{ revenue: 1 }], columns, {}, el), el);
  const title = el.querySelector("th.et-th .et-th-title");
  assert.equal(title.querySelectorAll("br").length, 1);
  assert.equal(title.childNodes.length, 3);
  assert.equal(title.childNodes[0].textContent, "Revenue");
  assert.equal(title.childNodes[2].textContent, "(USD thousands)");
  renderer.destroy();
});

test("chip columns render a coloured, centred value", () => {
  const columns = [
    { name: "city", type: "string", align: "left" },
    {
      name: "aqi",
      type: "number",
      align: "center",
      viz: "chip",
      fmt: "num0",
      color_options: { color_scale: ["#16a34a", "#dc2626"], min: 0, max: 250 },
    },
  ];
  const rows = [
    { city: "A", aqi: 50 },
    { city: "B", aqi: 220 },
  ];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
  const chips = el.querySelectorAll("tbody .et-chip");
  assert.equal(chips.length, 2);
  assert.equal(chips[0].textContent, "50");
  // The fill comes from the colour scale; the text is a contrast colour.
  assert.match(chips[0].style.backgroundColor, /rgb\(/);
  assert.match(chips[0].style.color, /rgb\(/);
  assert.notEqual(chips[0].style.backgroundColor, chips[1].style.backgroundColor);
  const cell = el.querySelectorAll("tbody td")[1];
  assert.equal(cell.style.textAlign, "center");
  renderer.destroy();
});

test("a chip can take a conditional colour from another column", () => {
  const columns = [
    { name: "status", type: "string", viz: "chip", color_options: { conditional_colors: "status_color" } },
    { name: "status_color", type: "string" },
  ];
  const rows = [
    { status: "Good", status_color: "#16a34a" },
    { status: "Bad", status_color: "#dc2626" },
  ];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
  const chips = el.querySelectorAll("tbody .et-chip");
  assert.equal(chips.length, 2);
  // No numeric range is needed for conditional colours.
  assert.equal(chips[0].style.backgroundColor, "rgb(22, 163, 74)");
  assert.equal(chips[1].style.backgroundColor, "rgb(220, 38, 38)");
  assert.equal(chips[0].style.color, "rgb(255, 255, 255)");
  renderer.destroy();
});

test("a column highlight paints the header and every cell", () => {
  const columns = [
    { name: "country", type: "string", align: "left" },
    { name: "y20", type: "number", fmt: "num0", highlight: "#fde8d0" },
    { name: "y21", type: "number", fmt: "num0" },
  ];
  const rows = [{ country: "A", y20: 1, y21: 2 }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
  const th = el.querySelectorAll("thead tr:last-child th")[1];
  assert.equal(th.style.backgroundColor, "rgb(253, 232, 208)");
  const td = el.querySelectorAll("tbody tr td")[1];
  assert.equal(td.style.backgroundColor, "rgb(253, 232, 208)");
  // The unhighlighted column is untouched.
  assert.equal(el.querySelectorAll("tbody tr td")[2].style.backgroundColor, "");
  renderer.destroy();
});

test("a spanner is highlighted only when every column it spans shares it", () => {
  const columns = [
    { name: "a", type: "number", column_group: "All", highlight: "#eef2ff" },
    { name: "b", type: "number", column_group: "All", highlight: "#eef2ff" },
    { name: "c", type: "number", column_group: "Some", highlight: "#eef2ff" },
    { name: "d", type: "number", column_group: "Some" },
  ];
  const rows = [{ a: 1, b: 2, c: 3, d: 4 }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
  assert.equal(el.querySelector('[data-group="All"]').style.backgroundColor, "rgb(238, 242, 255)");
  assert.equal(el.querySelector('[data-group="Some"]').style.backgroundColor, "");
  renderer.destroy();
});

test("a chip can have a minimum width but still grows", () => {
  const columns = [{ name: "status", type: "string", viz: "chip", chip_options: { min_width: 72 } }];
  const renderer = new EvidentialTableRenderer(makeModel([{ status: "Good" }], columns, {}, el), el);
  const chip = el.querySelector("tbody .et-chip");
  assert.equal(chip.style.minWidth, "72px");
  renderer.destroy();

  const css = [{ name: "status", type: "string", viz: "chip", chip_options: { min_width: "5rem" } }];
  const renderer2 = new EvidentialTableRenderer(makeModel([{ status: "Good" }], css, {}, el), el);
  assert.equal(el.querySelector("tbody .et-chip").style.minWidth, "5rem");
  renderer2.destroy();
});

test("a selectable row sets the selected trait and saves it", () => {
  const columns = [
    { name: "country", type: "string", align: "left" },
    { name: "revenue", type: "number", fmt: "usd0" },
  ];
  const rows = [
    { country: "Australia", revenue: 100 },
    { country: "Canada", revenue: 200 },
  ];
  const model = makeModel(rows, columns, { select: "country" }, el);
  const renderer = new EvidentialTableRenderer(model, el);
  const body = el.querySelectorAll("tbody tr");
  assert.ok(body[0].classList.contains("et-row-selectable"));
  body[1].dispatchEvent(new dom.window.MouseEvent("click", { bubbles: true }));
  assert.deepEqual(model.calls, [["set", "selected", "Canada"], ["save_changes"]]);
  // Clicking the selected row again clears the selection.
  model.data.selected = "Canada";
  renderer.render();
  const selected = el.querySelectorAll("tbody tr")[1];
  assert.ok(selected.classList.contains("et-row-selected"));
  selected.dispatchEvent(new dom.window.MouseEvent("click", { bubbles: true }));
  assert.deepEqual(model.calls.at(-2), ["set", "selected", null]);
  renderer.destroy();
});

test("rows are only selectable when `select` is set", () => {
  const model = makeModel(ROWS, COLUMNS, {}, el);
  const renderer = new EvidentialTableRenderer(model, el);
  assert.equal(el.querySelectorAll(".et-row-selectable").length, 0);
  renderer.destroy();
});

test("column info shows a native tooltip on the whole header cell", () => {
  const columns = [{ name: "city", type: "string", info: "A helpful hint" }];
  const renderer = new EvidentialTableRenderer(makeModel([{ city: "NYC" }], columns, {}, el), el);
  const th = el.querySelector("th.et-th");
  const icon = th.querySelector(".et-th-info");
  assert.ok(icon);
  assert.equal(icon.getAttribute("aria-label"), "A helpful hint");
  // The native tooltip lives on the cell, so hovering anywhere in it works.
  assert.equal(th.getAttribute("title"), "A helpful hint");
  assert.equal(icon.getAttribute("title"), null);
  renderer.destroy();
});

test("page_size 'all' shows every row without pagination", () => {
  const rows = Array.from({ length: 25 }, (_, i) => ({ city: `C${i}`, trips: i, revenue: i * 10 }));
  const renderer = new EvidentialTableRenderer(makeModel(rows, COLUMNS, { page_size: "all" }, el), el);
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
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { column_stats: true }, el), el);
  const first = el.querySelector("thead .et-stats-row");
  assert.ok(first, "statistics are header metadata outside the data body");
  assert.equal(el.querySelectorAll("tbody tr").length, rows.length);
  const cells = first.querySelectorAll(".et-stats-cell");
  assert.equal(cells.length, 2);
  assert.match(cells[0].textContent, /STRING \(nulls = 0\)/);
  assert.match(cells[0].textContent, /"city"/);
  assert.match(cells[0].textContent, /distinct: 3/);
  assert.match(cells[1].textContent, /NUMBER \(nulls = 1\)/);
  assert.match(cells[1].textContent, /"trips"/);
  assert.match(cells[1].textContent, /min: 90/);
  assert.match(cells[1].textContent, /max: 120/);
  assert.match(cells[1].textContent, /avg: 105/);
  renderer.destroy();
});

test("column statistics report boolean true/false counts", () => {
  const columns = [{ name: "active", type: "boolean" }];
  const rows = [{ active: true }, { active: true }, { active: false }, { active: null }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { column_stats: true }, el), el);
  const cell = el.querySelector(".et-stats-cell");
  assert.match(cell.textContent, /BOOLEAN \(nulls = 1\)/);
  assert.match(cell.textContent, /"active"/);
  assert.match(cell.textContent, /true: 2/);
  assert.match(cell.textContent, /false: 1/);
  renderer.destroy();
});

test("column statistics are off unless requested", () => {
  const renderer = new EvidentialTableRenderer(makeModel(ROWS, COLUMNS, {}, el), el);
  assert.equal(el.querySelector(".et-stats-row"), null);
  renderer.destroy();
});

test("logo columns render a logo.dev image", () => {
  const columns = [
    { name: "company", type: "string", logo: "domain" },
    { name: "domain", type: "string", hide: true },
  ];
  const rows = [{ company: "GitHub", domain: "github.com" }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
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
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
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
  const renderer = new EvidentialTableRenderer(
    makeModel(rows, columns, { group_type: "section", subtotal_position: "top" }, el),
    el,
  );
  const bodyRows = el.querySelectorAll("tbody tr");
  const usaCells = bodyRows[0].querySelectorAll("td");
  // country (rowspan), blank city placeholder, revenue — measures stay aligned.
  assert.equal(usaCells.length, 3);
  assert.equal(usaCells[0].getAttribute("rowspan"), "3");
  assert.equal(usaCells[1].textContent, "");
  assert.equal(usaCells[2].textContent, "$350");
  const detailCells = bodyRows[1].querySelectorAll("td");
  assert.equal(detailCells.length, 2); // country cell is covered
  assert.equal(detailCells[0].textContent, "NYC");
  renderer.destroy();
});

test("section total row keeps its measures aligned", () => {
  const columns = [
    { name: "country", type: "string", align: "left" },
    { name: "city", type: "string", align: "left" },
    { name: "revenue", type: "number", fmt: "usd0", align: "right" },
  ];
  const rows = [
    { country: "USA", city: "", revenue: 350, render_type: "row_subtotal", __level: 1, __group_key: '"USA"', __ancestors: [] },
    { country: "USA", city: "NYC", revenue: 100, render_type: "cell_data", __level: 2, __ancestors: ['"USA"'], __parent_key: '"USA"' },
    { country: "USA", city: "LA", revenue: 250, render_type: "cell_data", __level: 2, __ancestors: ['"USA"'], __parent_key: '"USA"' },
    { country: "All", city: "", revenue: 350, render_type: "row_total", __level: 0 },
  ];
  const renderer = new EvidentialTableRenderer(
    makeModel(rows, columns, { group_type: "section", subtotal_position: "top" }, el),
    el,
  );
  const total = [...el.querySelectorAll("tbody tr")].at(-1);
  const cells = total.querySelectorAll("td");
  assert.equal(cells.length, 3);
  assert.equal(cells[0].textContent, "All");
  assert.equal(cells[1].textContent, "");
  assert.equal(cells[2].textContent, "$350");
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
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
  const section = el.querySelector(".et-row-section td");
  assert.ok(section);
  assert.equal(section.getAttribute("colspan"), "3");
  assert.equal(section.textContent, "Section header");
  renderer.destroy();
});

test("caption renders below the table", () => {
  const renderer = new EvidentialTableRenderer(
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
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
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
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
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
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
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
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
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
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { rules }, el), el);
  const firstTrips = el.querySelectorAll("tbody tr")[0].querySelectorAll("td")[1];
  assert.equal(firstTrips.style.color, "rgb(185, 28, 28)");
  assert.equal(firstTrips.textContent, "12,000");
  renderer.destroy();
});

test("inline markdown renders in the title", () => {
  const renderer = new EvidentialTableRenderer(
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
  const renderer = new EvidentialTableRenderer(
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
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { rules }, el), el);
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
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
  const cells = [...el.querySelectorAll("tbody .et-cell-value")].map((cell) => cell.textContent);
  assert.equal(cells[2], "10–20");
  renderer.destroy();
});

test("markdown columns render inline markdown", () => {
  const columns = [{ name: "label", type: "string", markdown: true }];
  const rows = [{ label: "**Hi** there" }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
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
  const renderer = new EvidentialTableRenderer(
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
  const renderer = new EvidentialTableRenderer(
    makeModel(rows, columns, { align_decimals: true }, el),
    el,
  );
  const cells = [...el.querySelectorAll("tbody .et-cell-value")].map((cell) => cell.textContent);
  assert.deepEqual(cells, ["1.50", "12.25", "3.00"]);
  renderer.destroy();
});

test("font_size: absolute lengths and relative steps", () => {
  assert.equal(fontSizeValue("14px"), "14px");
  assert.equal(fontSizeValue("1rem"), "1rem");
  // A relative step adds N * 0.0625rem (1px) to the baseline.
  assert.equal(fontSizeValue("+2"), "calc(var(--et-font-size-base, 0.75rem) + 0.125rem)");
  assert.equal(fontSizeValue("-1"), "calc(var(--et-font-size-base, 0.75rem) + -0.0625rem)");
  assert.equal(fontSizeValue(2), "calc(var(--et-font-size-base, 0.75rem) + 0.125rem)");
  assert.equal(fontSizeValue(null), null);
});

test("title='' gives an empty header; bold/italic style the column", () => {
  const columns = [
    { name: "line_item", type: "string", title: "", font_weight: "600", font_style: "italic" },
  ];
  const renderer = new EvidentialTableRenderer(makeModel([{ line_item: "Widget" }], columns, {}, el), el);
  const th = el.querySelector("thead th");
  // An empty title must NOT fall back to the formatted column name.
  assert.ok(!th.textContent.includes("Line Item"), th.textContent);
  const td = el.querySelector("tbody td");
  assert.equal(td.style.fontWeight, "600");
  assert.equal(td.style.fontStyle, "italic");
  renderer.destroy();
});

test("neg colours, recolours and brackets negatives", () => {
  const columns = [
    {
      name: "n",
      type: "number",
      fmt: "usd0",
      red_negatives: true,
      bracket_negatives: true,
      negative_color: "#b91c1c",
      align: "right",
    },
  ];
  const rows = [{ n: -1234 }, { n: 42 }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
  const cells = [...el.querySelectorAll("tbody .et-cell-value")];
  assert.equal(cells[0].textContent, "($1,234)");
  assert.ok(cells[0].classList.contains("et-negative"));
  assert.equal(cells[0].style.color, "rgb(185, 28, 28)");
  assert.equal(cells[1].textContent, "$42");
  assert.ok(!cells[1].classList.contains("et-negative"));
  renderer.destroy();
});

test("bar pad sets --et-bar-pad for the bar and the line ends", () => {
  const columns = [
    {
      name: "gdp",
      type: "number",
      fmt: "num1",
      viz: "bar",
      align: "right",
      bar_options: { center: true, pad: 4, bar_color: "#0ea5e9" },
    },
  ];
  const rows = [{ gdp: 10 }, { gdp: -5 }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
  const cell = el.querySelector("tbody .et-bar-cell");
  assert.equal(cell.style.getPropertyValue("--et-bar-pad"), "4px");
  // The axis carries no inline inset; CSS applies it on the first/last rows.
  const axis = cell.querySelector(".et-bar-axis");
  assert.equal(axis.style.top, "");
  assert.equal(axis.style.bottom, "");
  renderer.destroy();
});

test("symbols with shape draw a CSS box, not a glyph", () => {
  const columns = [
    {
      name: "n",
      type: "number",
      viz: "symbols",
      align: "left",
      symbol_options: { shape: "square", color: "#f0a500", size: 0.8 },
    },
  ];
  const renderer = new EvidentialTableRenderer(makeModel([{ n: 3 }], columns, {}, el), el);
  const boxes = [...el.querySelectorAll("tbody .et-symbol-box")];
  assert.equal(boxes.length, 3);
  assert.ok(boxes[0].classList.contains("et-symbol-box-square"));
  assert.equal(boxes[0].style.width, "0.8em");
  assert.equal(boxes[0].style.backgroundColor, "rgb(240, 165, 0)");
  assert.equal(el.querySelectorAll("tbody .et-symbol").length, 0);
  renderer.destroy();
});

test("symbols repeat a glyph with empty slots and the right alignment", () => {
  const columns = [
    {
      name: "n",
      type: "number",
      viz: "symbols",
      align: "center",
      symbol_options: { symbol: "★", empty: "☆", max: 5, color: "#f59e0b" },
    },
  ];
  const rows = [{ n: 3 }, { n: 0 }, { n: 7 }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
  const cells = [...el.querySelectorAll("tbody .et-symbols")];
  assert.equal(cells[0].textContent, "★★★☆☆");
  assert.equal(cells[0].querySelectorAll(".et-symbol").length, 5);
  assert.equal(cells[1].textContent, "☆☆☆☆☆");
  // `max` is a floor on the slot count: a larger value simply draws more.
  assert.equal(cells[2].textContent, "★★★★★★★");
  assert.equal(cells[0].querySelector(".et-symbol").style.color, "rgb(245, 158, 11)");
  renderer.destroy();
});

test("symbols without max repeat the value exactly", () => {
  const columns = [
    { name: "n", type: "number", viz: "symbols", symbol_options: { symbol: "■", color: "#2EC1D3" } },
  ];
  const renderer = new EvidentialTableRenderer(makeModel([{ n: 3 }], columns, {}, el), el);
  const cell = el.querySelector("tbody .et-symbols");
  assert.equal(cell.querySelectorAll(".et-symbol").length, 3);
  assert.equal(cell.textContent, "■■■");
  renderer.destroy();
});

test("centered bar grows left/right from a centre line, label opposite", () => {
  const columns = [
    {
      name: "gdp",
      type: "number",
      fmt: "num1",
      viz: "bar",
      align: "right",
      bar_options: { center: true, bar_color: "#0ea5e9", bar_color_negative: "#0ea5e9" },
    },
  ];
  const rows = [{ gdp: 10 }, { gdp: -5 }, { gdp: 0 }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
  const cells = [...el.querySelectorAll("tbody .et-bar-cell")];
  assert.ok(cells[0].classList.contains("et-bar-center"));
  assert.ok(cells[0].querySelector(".et-bar-axis"));
  assert.ok(cells[0].querySelector(".et-bar").classList.contains("et-bar-right"));
  assert.ok(cells[1].querySelector(".et-bar").classList.contains("et-bar-left"));
  // The value sits on the opposite side of the centre line.
  assert.ok(cells[0].querySelector(".et-bar-label").classList.contains("et-bar-label-left"));
  assert.ok(cells[1].querySelector(".et-bar-label").classList.contains("et-bar-label-right"));
  // Half the cell per side: 10/10 -> 50%, |−5|/10 -> 25%.
  assert.equal(cells[0].querySelector(".et-bar").style.width, "50%");
  assert.equal(cells[1].querySelector(".et-bar").style.width, "25%");
  renderer.destroy();
});

test("direction='left' fills from the right, with a reference rule and per-row colour", () => {
  const columns = [
    {
      name: "spend",
      type: "number",
      fmt: "num1",
      viz: "bar",
      bar_options: {
        direction: "left",
        reference: 4,
        reference_label: "median",
        bar_color_column: "color",
      },
    },
  ];
  const rows = [
    { spend: 20, color: "#d9a01c" },
    { spend: 4, color: "#3a9b9b" },
    { spend: 0, color: "#b23a2e" },
  ];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {}, el), el);
  const cells = [...el.querySelectorAll("tbody .et-bar-cell")];
  const bar = cells[0].querySelector(".et-bar");
  // The bar fills from the right — the mirror of the default.
  assert.ok(bar.classList.contains("et-bar-fill-left"));
  assert.equal(bar.style.width, "100%"); // 20 / 20
  // Each bar takes its colour from the row's `color` column.
  assert.notEqual(
    bar.style.backgroundColor,
    cells[1].querySelector(".et-bar").style.backgroundColor,
  );
  // A benchmark rule at 4/20 of the scale, mirrored with the leftward bar.
  assert.equal(cells[0].querySelector(".et-bar-reference").style.left, "80%");
  assert.equal(cells[0].querySelector(".et-bar-reference-label").textContent, "median");
  renderer.destroy();
});

test("align_decimals leaves an explicit percent precision alone", () => {
  // Regression: `pct1` was padded to `pct3` from the raw fraction's decimals.
  const columns = [{ name: "share", type: "number", fmt: "pct1", align: "right" }];
  const rows = [{ share: 0.45 }, { share: 0.1115 }, { share: 0.0004 }];
  const renderer = new EvidentialTableRenderer(
    makeModel(rows, columns, { align_decimals: true }, el),
    el,
  );
  const cells = [...el.querySelectorAll("tbody .et-cell-value")].map((cell) => cell.textContent);
  assert.deepEqual(cells, ["45.0%", "11.2%", "0.0%"]);
  renderer.destroy();
});

test("stretch=false keeps the table content-sized", () => {
  const renderer = new EvidentialTableRenderer(
    makeModel(ROWS, COLUMNS, { stretch: false }, el),
    el,
  );
  assert.ok(el.querySelector(".et-root").classList.contains("et-stretch-off"));
  renderer.destroy();
});

test("row_shading supports group sizes (3,3)", () => {
  const rows = Array.from({ length: 6 }, (_, i) => ({ city: `C${i}`, trips: i, revenue: i * 10 }));
  const renderer = new EvidentialTableRenderer(makeModel(rows, COLUMNS, { row_shading: 3 }, el), el);
  const shaded = [...el.querySelectorAll("tbody tr")].map((tr) =>
    tr.classList.contains("et-row-shaded"),
  );
  assert.deepEqual(shaded, [false, false, false, true, true, true]);
  renderer.destroy();
});

test("row_shading pair sets shaded/unshaded counts", () => {
  const rows = Array.from({ length: 4 }, (_, i) => ({ city: `C${i}`, trips: i, revenue: i * 10 }));
  const renderer = new EvidentialTableRenderer(makeModel(rows, COLUMNS, { row_shading: [1, 3] }, el), el);
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

  const vertical = new EvidentialTableRenderer(
    makeModel(rows, columns, { rotate_titles: "vertical" }, el),
    el,
  );
  assert.equal(el.querySelectorAll(".et-th-vertical").length, 2);
  vertical.destroy();

  const oblique = new EvidentialTableRenderer(
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
  const renderer = new EvidentialTableRenderer(makeModel([{ v: 1234 }], columns, {}, el), el);
  const td = el.querySelector("tbody .et-td");
  assert.equal(td.style.fontVariantNumeric, "oldstyle-nums tabular-nums");
  renderer.destroy();
});

test("per-column font sets font-family", () => {
  const columns = [{ name: "v", type: "number", font: "'Hoefler Text', serif" }];
  const renderer = new EvidentialTableRenderer(makeModel([{ v: 1234 }], columns, {}, el), el);
  const td = el.querySelector("tbody .et-td");
  assert.match(td.style.fontFamily, /Hoefler/);
  renderer.destroy();
});

test("figure_style default uses the font's own figures", () => {
  const columns = [{ name: "v", type: "number", figure_style: "default" }];
  const renderer = new EvidentialTableRenderer(makeModel([{ v: 1234 }], columns, {}, el), el);
  assert.equal(el.querySelector("tbody .et-td").style.fontVariantNumeric, "normal");
  renderer.destroy();
});

test("no viz badge is added to headers", () => {
  const columns = [{ name: "v", type: "number", viz: "bar", bar_options: {} }];
  const renderer = new EvidentialTableRenderer(makeModel([{ v: 1 }], columns, {}, el), el);
  assert.equal(el.querySelectorAll(".et-viz-badge").length, 0);
  renderer.destroy();
});

test("theme.background drives the opaque expanded surface", () => {
  const renderer = new EvidentialTableRenderer(
    makeModel(ROWS, COLUMNS, { theme: { background: "#123456" } }, el),
    el,
  );
  const root = el.querySelector(".et-root");
  assert.equal(root.style.getPropertyValue("--et-surface"), "#123456");
  renderer.destroy();
});

test("three sub-columns share a sortable header and retain independent cell rendering", () => {
  const columns = [
    {name: "country", type: "string"},
    {name: "value", type: "number", fmt: "num1", align: "right", subcolumn_group: "Latest"},
    {name: "period", align: "left", font_color: "#808080", subcolumn_group: "Latest"},
    {name: "status", viz: "chip", align: "center", subcolumn_group: "Latest"},
  ];
  const rows = [
    {country: "A", value: 2, period: "Q3", status: "Stable"},
    {country: "B", value: 12.34, period: "Nov", status: "Rising"},
  ];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {row_numbers: true}, el), el);
  const header = el.querySelector(".et-th-subcolumns");
  assert.equal(header.textContent, "Latest");
  assert.equal(header.colSpan, 3);
  assert.equal(header.getAttribute("scope"), "colgroup");
  assert.equal(el.querySelectorAll("thead th").length, 3);
  const cells = [...el.querySelector("tbody tr").children];
  assert.deepEqual(cells.slice(2).map((cell) => cell.style.textAlign), ["right", "left", "center"]);
  assert.equal(cells[2].textContent, "2.0");
  assert.equal(cells[3].textContent, "Q3");
  assert.equal(cells[3].style.color, "rgb(128, 128, 128)");
  assert.ok(cells[4].querySelector(".et-chip"));
  assert.ok(cells[2].classList.contains("et-subcolumn-right"));
  assert.ok(!cells[2].classList.contains("et-subcolumn-left"));
  assert.ok(cells[3].classList.contains("et-subcolumn-left"));
  assert.ok(!cells[4].classList.contains("et-subcolumn-right"));
  assert.equal(cells[4].dataset.columnIndex, "4");
  assert.match(cells[2].getAttribute("aria-label"), /Latest: Value: 2.0/);
  header.dispatchEvent(new window.KeyboardEvent("keydown", {key: "Enter", bubbles: true}));
  assert.equal(el.querySelector("tbody tr td:nth-child(2)").textContent, "B");
  assert.equal(el.querySelector(".et-th-subcolumns").getAttribute("aria-sort"), "descending");
  assert.equal(document.activeElement, el.querySelector(".et-th-subcolumns"));
  renderer._state.hidden.add("period");
  renderer.render();
  assert.equal(el.querySelector(".et-th-subcolumns").colSpan, 2);
  renderer.destroy();
});

test("sub-column joins also apply to empty placeholders and summary statistics", () => {
  const columns = [
    {name: "value", type: "number", subcolumn_group: "Latest"},
    {name: "period", subcolumn_group: "Latest"},
  ];
  const model = makeModel([], columns, {empty_rows: 2, row_numbers: true, column_stats: true}, el);
  const renderer = new EvidentialTableRenderer(model, el);
  assert.equal(el.querySelectorAll(".et-row-placeholder .et-subcolumn-left").length, 2);
  model.set("rows", [{value: null, period: "Q3"}]);
  renderer.render();
  assert.equal(el.querySelector(".et-stats-cell").colSpan, 2);
  assert.equal(el.querySelector(".et-stats-cycle").textContent, "●○");
  assert.equal(el.querySelector(".et-null").closest("td").dataset.columnIndex, "1");
  renderer.destroy();
});

test("multiline parent headers render explicit breaks above shared sub-columns", () => {
  const columns = [
    {name: "value", column_group: "GDP\n% change on year ago:", subcolumn_group: "Latest"},
    {name: "period", column_group: "GDP\n% change on year ago:", subcolumn_group: "Latest"},
  ];
  const renderer = new EvidentialTableRenderer(makeModel([{value: 2.9, period: "Q3"}], columns, {}, el), el);
  const parent = el.querySelector(".et-th-group");
  assert.equal(parent.querySelectorAll("br").length, 1);
  assert.equal(parent.querySelectorAll(".et-th-line").length, 2);
  assert.equal(el.querySelector(".et-th-subcolumns").colSpan, 2);
  renderer.destroy();
});

test("font_color decorates nulls, templates and chips while location rules win", () => {
  const columns = [
    {name: "missing", font_color: "gray"},
    {name: "merged", template: "{value}", font_color: "gray"},
    {name: "status", viz: "chip", font_color: "gray"},
  ];
  const renderer = new EvidentialTableRenderer(makeModel([{value: "Q3", status: "Stable"}], columns, {
    rules: [{columns: ["merged"], style: {color: "red"}}],
  }, el), el);
  assert.deepEqual([...el.querySelectorAll("tbody td")].map((cell) => cell.style.color), ["gray", "red", "gray"]);
  renderer.destroy();
});

test("statistics cycle independently across shared headers and preserve state on redraw", () => {
  const columns = [
    {name: "city", type: "string"},
    {name: "value", type: "number", fmt: "num1", subcolumn_group: "Latest"},
    {name: "period", type: "string", subcolumn_group: "Latest"},
    {name: "status", type: "string", viz: "chip", subcolumn_group: "Latest"},
    {name: "forecast", type: "number", fmt: "num0"},
    {name: "rate", type: "number", column_group: "Other", subcolumn_group: "Latest"},
    {name: "month", type: "string", column_group: "Other", subcolumn_group: "Latest"},
  ];
  const rows = [
    {city: "A", value: 2.9, period: "Q3", status: "Stable", forecast: 4, rate: 1, month: "Nov"},
    {city: "B", value: 4.1, period: "Q3", status: null, forecast: 6, rate: 2, month: "Dec"},
  ];
  const model = makeModel(rows, columns, {column_stats: true, row_numbers: true, page_size: 1, select: "city"}, el);
  const renderer = new EvidentialTableRenderer(model, el);
  const cells = [...el.querySelectorAll(".et-stats-cell")];
  assert.deepEqual(cells.map((cell) => cell.colSpan), [1, 3, 1, 2]);
  assert.equal(el.querySelectorAll(".et-stats-footer").length, 5); // includes row numbers
  assert.equal(cells[0].querySelector(".et-stats-footer").textContent, "");
  assert.equal(cells[0].querySelector("button"), null);
  const buttons = el.querySelectorAll(".et-stats-cycle");
  assert.deepEqual([...buttons].map((button) => button.textContent), ["●○○", "●○"]);
  const renderCount = el.dataset.renderCount;
  const dataRow = el.querySelector(".et-row-selectable");
  buttons[0].focus();
  buttons[0].click();
  assert.equal(buttons[0].textContent, "○●○");
  assert.match(buttons[0].getAttribute("aria-label"), /Period, 2 of 3/);
  assert.match(cells[1].textContent, /distinct: 1/);
  assert.equal(cells[1].dataset.statsColumn, "period");
  assert.equal(document.activeElement, buttons[0]);
  assert.equal(el.dataset.renderCount, renderCount);
  assert.equal(el.querySelector(".et-row-selectable"), dataRow);
  buttons[0].click();
  assert.equal(buttons[0].textContent, "○○●");
  assert.match(cells[1].textContent, /nulls = 1/);
  buttons[1].click();
  assert.equal(cells[3].dataset.statsColumn, "month");
  renderer._gotoPage(1);
  assert.equal(el.querySelectorAll(".et-stats-cycle")[0].textContent, "○○●");
  assert.equal(el.querySelectorAll(".et-stats-cycle")[1].textContent, "○●");
  el.querySelector(".et-stats-cycle").click();
  assert.equal(el.querySelector(".et-stats-cycle").textContent, "●○○");
  assert.match(el.querySelectorAll(".et-stats-cell")[1].textContent, /avg: 3.5/);
  renderer._state.search = "A";
  renderer.render();
  assert.match(el.querySelectorAll(".et-stats-cell")[1].textContent, /avg: 3.5/);
  renderer.destroy();
});

test("statistics hide removed members, reset unavailable selections and omit singleton controls", () => {
  const columns = [
    {name: "a", type: "number", subcolumn_group: "Pair"},
    {name: "b", type: "string", subcolumn_group: "Pair"},
    {name: "single", subcolumn_group: "Only one"},
  ];
  const model = makeModel([{a: 2, b: "Q3", single: "x"}], columns, {column_stats: true}, el);
  const renderer = new EvidentialTableRenderer(model, el);
  el.querySelector(".et-stats-cycle").click();
  assert.equal(renderer._state.statsMembers.get("a"), "b");
  assert.equal(el.querySelectorAll(".et-stats-footer").length, 2);
  assert.equal(el.querySelectorAll(".et-stats-cell")[1].querySelector("button"), null);
  model.data.options = {column_stats: false};
  renderer.render();
  model.data.options = {column_stats: true};
  renderer.render();
  assert.equal(el.querySelector(".et-stats-cycle").textContent, "○●");
  renderer._state.hidden.add("b");
  renderer.render();
  assert.equal(el.querySelector(".et-stats-cell").dataset.statsColumn, "a");
  assert.equal(el.querySelectorAll(".et-stats-footer").length, 0);
  assert.equal(el.querySelector(".et-stats-cycle"), null);
  renderer._state.hidden.clear();
  model.data.columns = [{name: "replacement"}];
  renderer.render();
  assert.equal(renderer._state.statsMembers.size, 0);
  renderer.destroy();
});

test("adaptive footnote marks match cell and footer after collecting all unique notes", () => {
  const singles = ["*", "†", "‡", "§", "¶", "#", "+", "◆", "◇", "△"];
  for (const count of [10, 11, 12, 23]) {
    const expected = count === 10 ? singles : count === 11 ? ["*", "**", ...singles.slice(1)] :
      count === 12 ? ["*", "**", "†", "††", ...singles.slice(2)] :
      [...singles.flatMap((symbol) => [symbol, symbol + symbol]), "1", "2", "3"];
    const rows = Array.from({length: count}, (_, index) => ({value: index, note: `Note ${index}`, url: "/example"}));
    rows.push({...rows[0]}); // A repeated note must keep its mark without increasing the symbol budget.
    const renderer = new EvidentialTableRenderer(makeModel(rows, [
      {name: "value", footnote: "note", link: "url"},
    ], {page_size: "all", footnotes: ["An unmarked source note"]}, el), el);
    const marks = [...el.querySelectorAll("tbody .et-footnote-mark")];
    assert.deepEqual(marks.map((mark) => mark.textContent), [...expected, expected[0]]);
    assert.deepEqual([...el.querySelectorAll(".et-footnotes .et-footnote-mark")].map((mark) => mark.textContent), expected);
    assert.ok(marks.every((mark) => mark.tagName === "SUP" && !mark.closest("a")));
    assert.equal(el.querySelectorAll(".et-footnotes a").length, 0);
    renderer.destroy();
  }
});

test("paging recalculates the symbol budget for the currently displayed notes", () => {
  const rows = Array.from({length: 13}, (_, index) => ({value: index, note: `Note ${index}`}));
  const renderer = new EvidentialTableRenderer(makeModel(rows, [{name: "value", footnote: "note"}], {page_size: 11}, el), el);
  assert.equal(el.querySelectorAll("tbody .et-footnote-mark")[1].textContent, "**");
  renderer._gotoPage(1);
  assert.deepEqual([...el.querySelectorAll("tbody .et-footnote-mark")].map((mark) => mark.textContent), ["*", "†"]);
  renderer.destroy();
});

test("CSV download preserves search, indirect sorting, grouped column order and all matching pages", async (t) => {
  const columns = [
    {name: "city"},
    {name: "value", type: "number", sort_by: "rank", column_group: "Observation", subcolumn_group: "Latest"},
    {name: "forecast", type: "number"},
    {name: "period", column_group: "Observation", subcolumn_group: "Latest"},
    {name: "rank", type: "number", hide: true},
  ];
  const rows = [
    {city: 'keep "A",\nline', value: 2, forecast: 4, period: "Q3", rank: 9},
    {city: "keep B", value: 1, forecast: null, period: "Nov", rank: 1},
    {city: "drop C", value: 3, forecast: 5, period: "Dec", rank: 99},
  ];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, {
    title: "Clean Table", search: true, download: true, page_size: 1,
  }, el), el);
  const originalCreate = URL.createObjectURL;
  const originalRevoke = URL.revokeObjectURL;
  let blob;
  let clicked;
  const revoked = [];
  URL.createObjectURL = (value) => { blob = value; return "blob:csv-test"; };
  URL.revokeObjectURL = (value) => revoked.push(value);
  t.mock.method(window.HTMLAnchorElement.prototype, "click", function () {
    clicked = {href: this.href, filename: this.download};
  });
  t.after(() => {
    if (originalCreate === undefined) delete URL.createObjectURL;
    else URL.createObjectURL = originalCreate;
    if (originalRevoke === undefined) delete URL.revokeObjectURL;
    else URL.revokeObjectURL = originalRevoke;
    renderer.destroy();
  });
  const search = el.querySelector(".et-search");
  search.value = "keep";
  search.dispatchEvent(new window.Event("input", {bubbles: true}));
  el.querySelector('th[data-column="value"]').click();
  assert.equal(el.querySelectorAll("tbody tr").length, 1);
  el.querySelector(".et-download-btn").click();
  const csv = await new Promise((resolve, reject) => {
    const reader = new window.FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(reader.error);
    reader.readAsText(blob);
  });
  assert.equal(csv, 'City,Value,Period,Forecast\n"keep ""A"",\nline",2,Q3,4\nkeep B,1,Nov,');
  assert.deepEqual(clicked, {href: "blob:csv-test", filename: "clean_table.csv"});
  assert.deepEqual(revoked, ["blob:csv-test"]);
});

test("CSV exports matching details in layout order without headings or summaries", async (t) => {
  const data = [{city: "A", value: 1}, {city: "B", value: 20}, {city: "C", value: 10}];
  const model = makeModel(data, [{name: "city"}, {name: "value", type: "number"}], {page_size: 1}, el);
  model.data.row_layout = {version: 1, groups: [
    {id: "first", members: [0, 2], depth: 0, children: [], section: {label: "Group 1"}},
    {id: "second", members: [1], depth: 0, children: [], section: {label: "Group 2"}},
  ], grand_summary: {label: "Total", cells: {value: {operation: "sum", source: "value"}}}};
  const renderer = new EvidentialTableRenderer(model, el);
  let blob;
  const originalCreate = URL.createObjectURL;
  const originalRevoke = URL.revokeObjectURL;
  URL.createObjectURL = value => { blob = value; return "blob:test"; };
  URL.revokeObjectURL = () => {};
  t.after(() => {
    if (originalCreate === undefined) delete URL.createObjectURL;
    else URL.createObjectURL = originalCreate;
    if (originalRevoke === undefined) delete URL.revokeObjectURL;
    else URL.revokeObjectURL = originalRevoke;
    renderer.destroy();
  });
  t.mock.method(window.HTMLAnchorElement.prototype, "click", () => {});
  renderer._state.sort = {column: "value", direction: "desc"};
  renderer._downloadCsv();
  const csv = await new Promise(resolve => {
    const reader = new window.FileReader();
    reader.onload = () => resolve(reader.result);
    reader.readAsText(blob);
  });
  assert.equal(csv, "City,Value\nC,10\nA,1\nB,20");
  renderer.destroy();
});

test("marks encodings render overlaid bars with owned labels", () => {
  const rows = [
    { current: 8, previous: 5, candidate: "Alpha", target: 6 },
    { current: 3, previous: 7, candidate: "Beta", target: 6 },
  ];
  const columns = [{
    name: "current", type: "number", fmt: "num0",
    encodings: [
      { kind: "bar", source: "current", color: "#1d4ed8", size: 0.4, label: { source: "candidate" } },
      { kind: "bar", source: "previous", color: "#d1d5db", size: 0.8 },
    ],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const cells = [...el.querySelectorAll("tbody td")];
  assert.equal(cells.length, 2);
  const bars = cells[0].querySelectorAll(".et-mark-bar");
  assert.equal(bars.length, 2);
  // The wider "previous" bar sits behind the thinner "current" bar.
  assert.match(bars[0].style.height, /40%/);
  assert.match(bars[1].style.height, /80%/);
  // The label names the candidate field, not the value.
  assert.match(cells[0].textContent, /Alpha/);
  assert.match(cells[1].textContent, /Beta/);
  renderer.destroy();
});

test("marks colour and shared scale come from the column", () => {
  const rows = [
    { votes: 25, candidate: "A", colour: "#ff0000" },
    { votes: 75, candidate: "B", colour: "#00ff00" },
  ];
  const columns = [{
    name: "votes", type: "number",
    scale: { domain: [0, 100] },
    encodings: [{ kind: "bar", source: "votes", color_column: "colour" }],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const bars = [...el.querySelectorAll(".et-mark-bar")];
  assert.equal(bars.length, 2);
  // 25/100 and 75/100 of the shared domain.
  assert.match(bars[0].style.width, /25%/);
  assert.match(bars[1].style.width, /75%/);
  assert.notEqual(bars[0].style.backgroundColor, bars[1].style.backgroundColor);
  renderer.destroy();
});

test("point and range marks share the column's bar scale", () => {
  const rows = [{ estimate: 20, low: 10, high: 40, target: 30 }];
  const columns = [{
    name: "estimate", type: "number",
    encodings: [
      { kind: "range", source: "low", high: "high", cap: "line" },
      { kind: "point", source: "estimate" },
      { kind: "point", source: "target", size: 9 },
    ],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const cell = el.querySelector("tbody td");
  assert.ok(cell.querySelector(".et-mark-range"));
  assert.equal(cell.querySelectorAll(".et-mark-point").length, 2);
  assert.equal(cell.querySelectorAll(".et-mark-cap").length, 2);
  renderer.destroy();
});

test("reference lines render at the shared scale", () => {
  const rows = [{ debt: 40 }, { debt: 80 }];
  const columns = [{
    name: "debt", type: "number",
    scale: { domain: [0, 100] },
    references: [{ value: 50, label: "Average" }],
    encodings: [{ kind: "bar", source: "debt" }],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const rule = el.querySelector(".et-mark-reference");
  assert.ok(rule);
  assert.match(rule.style.left, /50%/);
  assert.match(el.textContent, /Average/);
  renderer.destroy();
});

test("stacked_bar renders cumulative segments from the row total", () => {
  const rows = [
    { a: 10, b: 20, c: 10 },
    { a: 5, b: 5, c: 10 },
  ];
  const columns = [{
    name: "a", type: "number",
    encodings: [
      { kind: "stacked_bar", source: "a", color: "#111" },
      { kind: "stacked_bar", source: "b", color: "#222" },
      { kind: "stacked_bar", source: "c", color: "#333" },
    ],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const segs = [...el.querySelectorAll(".et-mark-stack-seg")];
  assert.equal(segs.length, 6);
  // Row 1 total 40: 10/40, 20/40, 10/40.
  assert.match(segs[0].style.width, /25%/);
  assert.match(segs[1].style.width, /50%/);
  assert.match(segs[2].style.width, /25%/);
  renderer.destroy();
});

test("stacked_bar normalize='percent' uses each row's share", () => {
  const rows = [{ a: 1, b: 3 }];
  const columns = [{
    name: "a", type: "number",
    scale: { normalize: "percent" },
    encodings: [
      { kind: "stacked_bar", source: "a" },
      { kind: "stacked_bar", source: "b" },
    ],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const segs = [...el.querySelectorAll(".et-mark-stack-seg")];
  assert.match(segs[0].style.width, /25%/);
  assert.match(segs[1].style.width, /75%/);
  renderer.destroy();
});

test("strip renders one coloured segment per ordered category", () => {
  const rows = [{ form: ["W", "D", "L", "W"] }];
  const columns = [{
    name: "form", type: "array",
    encodings: [{
      kind: "strip", source: "form",
      colors: { W: "#16a34a", D: "#9ca3af", L: "#dc2626" },
      strip_labels: true, segmented: true,
    }],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const segs = [...el.querySelectorAll(".et-strip-seg")];
  assert.equal(segs.length, 4);
  assert.notEqual(segs[0].style.backgroundColor, segs[1].style.backgroundColor);
  assert.equal(el.querySelectorAll(".et-strip-label").length, 4);
  renderer.destroy();
});

test("boxplot renders a whisker, IQR box, median and outliers", () => {
  const rows = [{ lo: 0, q1: 10, med: 12, q3: 15, hi: 30, outs: [40, -5] }];
  const columns = [{
    name: "med", type: "number",
    scale: { domain: [-10, 45] },
    encodings: [{ kind: "boxplot", source: "med", parts: { minimum: "lo", q1: "q1", median: "med", q3: "q3", maximum: "hi" }, outliers: "outs", whisker: "iqr" }],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  assert.ok(el.querySelector(".et-box-whisker"));
  assert.ok(el.querySelector(".et-box-iqr"));
  assert.ok(el.querySelector(".et-box-median"));
  assert.equal(el.querySelectorAll(".et-box-cap").length, 2);
  assert.equal(el.querySelectorAll(".et-box-outlier").length, 2);
  renderer.destroy();
});

test("diverging stacked_bar splits the neutral segment around the origin", () => {
  const rows = [{ sd: 10, d: 20, n: 30, a: 25, sa: 15 }];
  const columns = [{
    name: "sd", type: "number",
    encodings: [
      { kind: "stacked_bar", source: "sd", diverge_at: "n", neutral: "split" },
      { kind: "stacked_bar", source: "d" },
      { kind: "stacked_bar", source: "n" },
      { kind: "stacked_bar", source: "a" },
      { kind: "stacked_bar", source: "sa" },
    ],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const segs = [...el.querySelectorAll(".et-mark-stack-seg")];
  // Neutral contributes two halves; the four other categories stay whole.
  assert.equal(segs.length, 6);
  // Left arm total = 10 + 20 + 15 = 45; right = 15 + 25 + 15 = 55; max 55.
  const leftSide = segs.filter((seg) => parseFloat(seg.style.left) < 50);
  assert.ok(leftSide.length >= 3);
  renderer.destroy();
});

test("positioned strip maps runs to a shared x axis", () => {
  const rows = [
    { periods: [{ start: 0, end: 3, category: "expansion" }, { start: 3, end: 5, category: "recession" }] },
    { periods: [{ start: 1, end: 4, category: "expansion" }] },
  ];
  const columns = [{
    name: "periods", type: "array",
    encodings: [{ kind: "strip", source: "periods", colors: { expansion: "#16a34a", recession: "#dc2626" } }],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const runs = [...el.querySelectorAll(".et-strip-run")];
  assert.equal(runs.length, 3);
  // Shared domain 0..5: the first run spans 0..3 (60%).
  assert.match(runs[0].style.width, /60%/);
  renderer.destroy();
});

test("distribution draws a density band over the shared axis", () => {
  const rows = [{
    density: [
      { seats: 0, share: 0 },
      { seats: 5, share: 10 },
      { seats: 10, share: 4 },
      { seats: 15, share: 0 },
    ],
  }];
  const columns = [{
    name: "density", type: "array",
    encodings: [{ kind: "distribution", source: "density", distribution: {x: "seats", y: "share", height: 0.5, density_max: null} }],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const band = el.querySelector(".et-mark-distribution");
  assert.ok(band);
  assert.equal(band.style.height, "50%");
  assert.equal(band.querySelectorAll("svg, polygon, polyline").length, 0);
  assert.ok(band.querySelector(".et-density-band-run"));
  renderer.destroy();
});

test("log scale positions marks logarithmically", () => {
  const rows = [{ est: 10 }];
  const columns = [{
    name: "est", type: "number",
    scale: { domain: [1, 100], transform: "log" },
    encodings: [{ kind: "point", source: "est" }],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const dot = el.querySelector(".et-mark-point");
  // log10(10) is halfway between log10(1)=0 and log10(100)=2.
  assert.match(dot.style.left, /50%/);
  renderer.destroy();
});

test("range cap='arrow' marks endpoints beyond the domain", () => {
  const rows = [{ lo: 1, hi: 100 }];
  const columns = [{
    name: "lo", type: "number",
    scale: { domain: [0, 10] },
    encodings: [{ kind: "range", source: "lo", high: "hi", cap: "arrow" }],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  assert.ok(el.querySelector(".et-mark-arrow-end"));
  assert.equal(el.querySelectorAll(".et-mark-arrow").length, 1);
  renderer.destroy();
});

test("row_lines as a colour name drives the row border variable", () => {
  const renderer = new EvidentialTableRenderer(
    makeModel([{ a: 1 }], [{ name: "a" }], { row_lines: "grey" }, el), el,
  );
  assert.equal(renderer.root.style.getPropertyValue("--et-row-border"), "grey");
  renderer.destroy();
});

test("section rows honour center alignment", () => {
  const rows = [
    { a: "detail" },
    { render_type: "row_section", __label: "Divider", __align: "center" },
  ];
  const renderer = new EvidentialTableRenderer(makeModel(rows, [{ name: "a" }], {}, el), el);
  assert.ok(el.querySelector(".et-section-center"));
  renderer.destroy();
});

test("combined section+summary rows keep their values and a section rule", () => {
  const rows = [
    { g: "A", n: 1 },
    { g: "A", n: 2 },
    { render_type: "row_subtotal", __combined: true, __level: 1, __group_key: "A", g: "A", n: 3 },
  ];
  const renderer = new EvidentialTableRenderer(
    makeModel(rows, [{ name: "g" }, { name: "n", type: "number" }], {}, el), el,
  );
  const combined = el.querySelector(".et-row-combined");
  assert.ok(combined);
  assert.match(combined.textContent, /A/);
  assert.match(combined.textContent, /3/);
  renderer.destroy();
});

test("a section spanning a page repeats its label as a continuation", () => {
  const rows = [
    { render_type: "row_section", __label: "North" },
    { g: "d1", n: 1 }, { g: "d2", n: 2 }, { g: "d3", n: 3 }, { g: "d4", n: 4 }, { g: "d5", n: 5 },
  ];
  const renderer = new EvidentialTableRenderer(
    makeModel(rows, [{ name: "g" }, { name: "n", type: "number" }], { page_size: 3 }, el), el,
  );
  renderer._gotoPage(1);
  const cont = el.querySelector(".et-row-continuation");
  assert.ok(cont);
  assert.match(cont.textContent, /North \(cont\.\)/);
  renderer.destroy();
});

test("reference bands shade a column-wide zone", () => {
  const rows = [{ est: 1 }];
  const columns = [{
    name: "est", type: "number",
    scale: { domain: [0, 2] },
    references: [{ value: 0.8, high: 1.25, label: "equivalence" }],
    encodings: [{ kind: "point", source: "est" }],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const band = el.querySelector(".et-mark-band");
  assert.ok(band);
  // 0.8..1.25 of a 0..2 domain.
  assert.match(band.style.left, /40%/);
  assert.match(band.style.width, /22\.5%/);
  renderer.destroy();
});

test("points draws one marker per array observation", () => {
  const rows = [{ x: 1, observations: [1, 2, 3] }];
  const columns = [{
    name: "x", type: "number", scale: { domain: [0, 3] },
    encodings: [
      { kind: "bar", source: "x" },
      { kind: "points", source: "observations", size: 5 },
    ],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  assert.equal(el.querySelectorAll(".et-mark-point").length, 3);
  renderer.destroy();
});

test("sparkline points and markers draw filled dots", () => {
  const rows = [{ trend: [1, 2, 3] }];
  const columns = [{ name: "trend", type: "array", viz: "sparkline", sparkline_options: { type: "points" } }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const dots = [...el.querySelectorAll(".et-sparkline circle")];
  assert.equal(dots.length, 3);
  assert.notEqual(dots[0].getAttribute("fill"), "transparent");
  renderer.destroy();
});

test("signed sparkline area splits at the zero baseline", () => {
  const rows = [{ trend: [1, -1, 2] }];
  const columns = [{
    name: "trend", type: "array", viz: "sparkline",
    sparkline_options: { type: "area", signed: true },
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  assert.equal(el.querySelectorAll(".et-sparkline polygon").length, 2);
  renderer.destroy();
});

test("boolean cells render their symbols and labels", () => {
  const rows = [{ active: true }, { active: false }];
  const columns = [{
    name: "active", type: "boolean",
    boolean_options: { true_text: "Active", false_text: "Inactive", true_symbol: "✓", false_symbol: "✗" },
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const cells = [...el.querySelectorAll("tbody td")];
  assert.match(cells[0].textContent, /✓ Active/);
  assert.match(cells[1].textContent, /✗ Inactive/);
  assert.ok(cells[0].querySelector(".et-boolean-true"));
  renderer.destroy();
});

test("icon_map renders a glyph per category and falls back to text", () => {
  const rows = [{ signal: "buy" }, { signal: "unknown" }];
  const columns = [{ name: "signal", type: "string", icon_map: { buy: "▲", sell: "▼" } }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const cells = [...el.querySelectorAll("tbody td")];
  assert.equal(cells[0].querySelector(".et-icon-glyph").textContent, "▲");
  assert.match(cells[1].textContent, /unknown/);
  renderer.destroy();
});

test("section rows participate in alternating shading", () => {
  const rows = [
    { a: "one" },
    { render_type: "row_section", __label: "Group" },
    { a: "two" },
  ];
  const renderer = new EvidentialTableRenderer(
    makeModel(rows, [{ name: "a" }], { row_shading: true }, el), el,
  );
  const section = el.querySelector(".et-row-section");
  assert.ok(section);
  // The section row consumes a slot in the pattern, like a data row.
  assert.ok(section.classList.contains("et-row-shaded"));
  renderer.destroy();
});

test("spacer rows render a blank gap", () => {
  const rows = [{ a: "one" }, { render_type: "row_spacer", __height: 8 }, { a: "two" }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, [{ name: "a" }], {}, el), el);
  const spacer = el.querySelector(".et-row-spacer");
  assert.ok(spacer);
  assert.equal(spacer.textContent, "");
  renderer.destroy();
});

test("marks axis renders tick labels and gridlines", () => {
  const rows = [{ x: 20 }, { x: 80 }];
  const columns = [{
    name: "x", type: "number",
    scale: { domain: [0, 100], axis: true, gridlines: true },
    encodings: [{ kind: "bar", source: "x" }],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const ticks = [...el.querySelectorAll(".et-axis-tick")];
  assert.ok(ticks.length >= 3);
  assert.match(el.querySelector(".et-axis-row").textContent, /25/);
  assert.ok(el.querySelector(".et-mark-gridline"));
  renderer.destroy();
});

test("cell guides are clipped independently of marks, labels and interval arrows", () => {
  const model = makeModel([{x: 20, lo: -5, hi: 105}], [{name: "x", encodings: [
    {kind: "point", source: "x"}, {kind: "range", source: "lo", high: "hi", overflow: "arrow"}],
    scale: {domain: [0, 100], gridlines: true}, references: [{value: 50}]}], {}, el);
  const renderer = new EvidentialTableRenderer(model, el);
  const cell = el.querySelector("tbody td");
  assert.ok(cell.classList.contains("et-has-guides"));
  assert.equal(cell.querySelectorAll(".et-cell-guides .et-mark-gridline").length, 5);
  assert.equal(cell.querySelectorAll(".et-cell-guides .et-mark-reference").length, 1);
  assert.equal(cell.querySelectorAll(".et-marks .et-mark-gridline, .et-marks .et-mark-reference").length, 0);
  assert.equal(cell.querySelectorAll(".et-marks .et-mark-arrow").length, 2);
  assert.equal(cell.querySelector(".et-cell-guides").getAttribute("aria-hidden"), "true");
  renderer.destroy();
});

test("axes live outside the data body and only top-axis labels gain header height", () => {
  const columns = [
    {name: "country"},
    {name: "top", encodings: [{kind: "point", source: "top"}], scale: {axis: true}},
    {name: "bottom", encodings: [{kind: "point", source: "bottom"}], scale: {axis: true, axis_position: "bottom"}},
  ];
  const model = makeModel([{country: "A", top: 1, bottom: 2}, {country: "B", top: 3, bottom: 4}],
    columns, {row_numbers: true}, el);
  const renderer = new EvidentialTableRenderer(model, el);
  assert.equal(el.querySelectorAll("tbody tr").length, 2);
  assert.equal(el.querySelectorAll("tbody .et-axis").length, 0);
  assert.ok(el.querySelector("thead .et-axis-row-top"));
  assert.ok(el.querySelector("tfoot .et-axis-row-bottom"));
  assert.equal(el.querySelector('th[data-column="country"]').rowSpan, 2);
  assert.equal(el.querySelector('th[data-column="top"]').rowSpan, 1);
  assert.equal(el.querySelector('th[data-column="bottom"]').rowSpan, 2);
  assert.equal(el.querySelector(".et-axis-row").classList.contains("et-row"), false);
  renderer.destroy();
});

test("log axis uses a power-of-ten tick ladder", () => {
  const rows = [{ x: 10 }];
  const columns = [{
    name: "x", type: "number",
    scale: { domain: [1, 100], transform: "log", axis: true, gridlines: true },
    encodings: [{ kind: "point", source: "x" }],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const ticks = [...el.querySelectorAll(".et-axis-tick")].map((node) => node.textContent);
  assert.ok(ticks.some((tick) => tick.startsWith("10")));
  assert.ok(ticks.length >= 4);
  // log10(10) is the midpoint of the 1..100 domain.
  const middles = [...el.querySelectorAll(".et-axis-tick")].filter((node) => /50%/.test(node.style.left));
  assert.ok(middles.length >= 1);
  renderer.destroy();
});

test("mark valign places bars at the top or bottom of the cell", () => {
  const rows = [{ a: 3, b: 5 }];
  const columns = [{
    name: "a", type: "number",
    encodings: [
      { kind: "bar", source: "a", valign: "top", size: 0.4 },
      { kind: "bar", source: "b", valign: "bottom", size: 0.4 },
    ],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const bars = [...el.querySelectorAll(".et-mark-bar")];
  assert.match(bars[0].style.top, /^0/);
  assert.match(bars[1].style.bottom, /^0/);
  renderer.destroy();
});

test("mark labels apply a prefix and suffix", () => {
  const rows = [{ x: 12, name: "Alpha" }];
  const columns = [{
    name: "x", type: "number",
    encodings: [{ kind: "bar", source: "x", label: { value: true, prefix: "$", suffix: "m", format: "num0" } }],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  assert.match(el.querySelector(".et-mark-label").textContent, /\$12m/);
  renderer.destroy();
});

test("stacked bar label_align aligns segment text", () => {
  const rows = [{ a: 1, b: 1 }];
  const columns = [{
    name: "a", type: "number",
    encodings: [
      { kind: "stacked_bar", source: "a", label: { value: true, align: "begin" } },
      { kind: "stacked_bar", source: "b" },
    ],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const first = el.querySelector(".et-mark-stack-seg");
  assert.equal(first.style.justifyContent, "flex-start");
  renderer.destroy();
});

test("percent stack spans 0..100 and labels shares", () => {
  const rows = [{ a: 1, b: 3 }];
  const columns = [{
    name: "a", type: "number",
    scale: { normalize: "percent", axis: true },
    encodings: [
      { kind: "stacked_bar", source: "a", label: { value: true, share: true } },
      { kind: "stacked_bar", source: "b" },
    ],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const segs = [...el.querySelectorAll(".et-mark-stack-seg")];
  assert.match(segs[0].style.width, /25%/);
  assert.match(segs[1].style.width, /75%/);
  // The first segment labels its share, not its raw value.
  assert.match(segs[0].textContent, /25%/);
  // The axis is a 0..100 percent scale.
  const ticks = [...el.querySelectorAll(".et-axis-tick")].map((node) => node.textContent);
  assert.ok(ticks.some((tick) => tick.startsWith("100")));
  renderer.destroy();
});

test("diverging percent stack centres the neutral segment", () => {
  const rows = [{ sd: 10, d: 20, n: 30, a: 25, sa: 15 }];
  const columns = [{
    name: "sd", type: "number",
    scale: { normalize: "percent" },
    encodings: [
      { kind: "stacked_bar", source: "sd", diverge_at: "n", neutral: "split" },
      { kind: "stacked_bar", source: "d" },
      { kind: "stacked_bar", source: "n" },
      { kind: "stacked_bar", source: "a" },
      { kind: "stacked_bar", source: "sa" },
    ],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const segs = [...el.querySelectorAll(".et-mark-stack-seg")];
  assert.equal(segs.length, 6);
  // The neutral half starts at the centre (50%).
  const centre = segs.find((seg) => /50%/.test(seg.style.left));
  assert.ok(centre);
  renderer.destroy();
});

test("stacked bar size sets the stack height", () => {
  const rows = [{ a: 1, b: 1 }];
  const columns = [{
    name: "a", type: "number",
    encodings: [
      { kind: "stacked_bar", source: "a", size: 0.4 },
      { kind: "stacked_bar", source: "b", size: 0.4 },
    ],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const stack = el.querySelector(".et-mark-stack");
  assert.match(stack.style.top, /30%/);
  renderer.destroy();
});

test("cell_style sets cell chrome and a per-row background", () => {
  const rows = [{ x: 1, bg: "#fee2e2" }, { x: 2, bg: "#dcfce7" }];
  const columns = [
    { name: "x", type: "number", cell_style: { background_column: "bg", color: "#111", border: "1px solid red" } },
  ];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const cells = [...el.querySelectorAll("tbody td")];
  assert.notEqual(cells[0].style.backgroundColor, "");
  assert.notEqual(cells[0].style.backgroundColor, cells[1].style.backgroundColor);
  assert.equal(cells[0].style.border, "1px solid red");
  renderer.destroy();
});

test("sparkline markers='ends' draws only the endpoints", () => {
  const rows = [{ trend: [1, 2, 3] }];
  const columns = [{
    name: "trend", type: "array", viz: "sparkline",
    sparkline_options: { type: "line", markers: "ends", marker_color: "#f00" },
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const dots = [...el.querySelectorAll(".et-sparkline circle")];
  assert.notEqual(dots[0].getAttribute("fill"), "transparent");
  assert.equal(dots[1].getAttribute("fill"), "transparent");
  assert.notEqual(dots[2].getAttribute("fill"), "transparent");
  assert.equal(dots[0].getAttribute("fill"), "#f00");
  renderer.destroy();
});

test("sparkline per-point colour overrides marker_color", () => {
  const rows = [{ trend: [{ x: 0, y: 1, color: "#00f" }, { x: 1, y: 2 }] }];
  const columns = [{
    name: "trend", type: "array", viz: "sparkline",
    sparkline_options: { type: "line", markers: true, marker_color: "#0f0" },
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const dots = [...el.querySelectorAll(".et-sparkline circle")];
  assert.equal(dots[0].getAttribute("fill"), "#00f");
  assert.equal(dots[1].getAttribute("fill"), "#0f0");
  renderer.destroy();
});

test("multiple stub columns are marked as the row-label area", () => {
  const rows = [{ region: "North", country: "Canada", x: 1 }];
  const columns = [{ name: "region" }, { name: "country" }, { name: "x", type: "number" }];
  const renderer = new EvidentialTableRenderer(
    makeModel(rows, columns, { stub: ["region", "country"] }, el), el,
  );
  assert.equal(el.querySelectorAll("td.et-stub").length, 2);
  assert.equal(el.querySelectorAll("th.et-stub-head").length, 2);
  renderer.destroy();
});

test("range fill draws a translucent band", () => {
  const rows = [{ estimate: 20, low: 10, high: 40 }];
  const columns = [{
    name: "estimate", type: "number",
    scale: { domain: [0, 50] },
    encodings: [
      { kind: "range", source: "low", high: "high", fill: true, color: "#8b5cf6" },
      { kind: "point", source: "estimate" },
    ],
  }];
  const renderer = new EvidentialTableRenderer(makeModel(rows, columns, { page_size: 10 }, el), el);
  const band = el.querySelector(".et-mark-range-fill");
  assert.ok(band);
  assert.match(band.style.width, /60%/);
  renderer.destroy();
});
