import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import { HoldController, holdInterval } from "./src/interactions.js";
import { LoadingController } from "./src/loading.js";
import { TableViewport } from "./src/viewport.js";

const dom = new JSDOM("<body></body>");
global.window = dom.window;
global.ResizeObserver = class { observe() {} unobserve() {} disconnect() {} };

test("stopping a hold disposes repeat timers and release handlers", (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  let calls = 0;
  const controller = new HoldController(() => { calls++; return true; });
  controller.start("next");
  t.mock.timers.tick(700);
  assert.equal(calls, 1);
  assert.equal(controller.consumeClick(), true);
  assert.equal(controller.consumeClick(), false);
  window.dispatchEvent(new window.Event("pointerup"));
  t.mock.timers.tick(5000);
  assert.equal(calls, 1);
});

test("disposing loading prevents deferred changes to removed nodes", (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  const root = dom.window.document.createElement("div");
  const overlay = dom.window.document.createElement("div");
  const controller = new LoadingController(root, overlay, root);
  controller.set(true);
  controller.destroy();
  t.mock.timers.tick(1000);
  assert.equal(root.classList.contains("et-loading"), false);
});

test("viewport disposal cancels pending layout work", (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  global.requestAnimationFrame = (callback) => setTimeout(callback, 1);
  global.cancelAnimationFrame = clearTimeout;
  const scroller = dom.window.document.createElement("div");
  const viewport = new TableViewport({ scroller, getOptions: () => ({}) });
  let calls = 0;
  viewport.frame(() => calls++);
  viewport.destroy();
  t.mock.timers.tick(1000);
  assert.equal(calls, 0);
  assert.equal(viewport.frames.size, 0);
});

test("frozen offsets use physical columns and preserve nested header heights", () => {
  const scroller = dom.window.document.createElement("div");
  scroller.innerHTML = `<table><thead>
    <tr><th data-column-start="0" colspan="4">Economy</th></tr>
    <tr><th data-column-start="0">Country</th><th data-column-start="1" colspan="3">Latest</th></tr>
    </thead><tbody><tr>${[0,1,2,3].map((i) => `<td data-column-index="${i}">${i}</td>`).join("")}</tr></tbody></table>`;
  scroller.querySelector("table").getBoundingClientRect = () => ({left: 10});
  const rows = scroller.querySelectorAll("thead tr");
  rows[0].getBoundingClientRect = () => ({height: 25});
  rows[1].getBoundingClientRect = () => ({height: 30});
  for (const [index, cell] of [...scroller.querySelectorAll("td")].entries()) {
    cell.getBoundingClientRect = () => ({left: [10, 110, 150, 180][index]});
  }
  const options = {freeze_columns: 3};
  const viewport = new TableViewport({scroller, getOptions: () => options});
  viewport.applyFrozenOffsets();
  assert.deepEqual([...scroller.querySelectorAll("td")].map((cell) => cell.style.left), ["0px", "100px", "140px", ""]);
  assert.equal(rows[1].children[0].style.top, "25px");
  assert.ok(!rows[1].children[1].classList.contains("et-frozen"));
  options.freeze_columns = 4;
  viewport.applyFrozenOffsets();
  assert.equal(rows[1].children[1].style.left, "100px");
  assert.ok(rows[0].children[0].classList.contains("et-frozen"));
  viewport.destroy();
});

test("hold repeat interval eases from 700ms to 100ms by 3s", () => {
  assert.equal(holdInterval(0), 700);
  assert.equal(holdInterval(700), 700);
  assert.equal(holdInterval(1850), 400);
  assert.equal(holdInterval(3000), 100);
  assert.equal(holdInterval(10000), 100);
});

test("fully closed groups still have frozen column headers without indexed body cells", () => {
  const scroller = dom.window.document.createElement("div");
  scroller.innerHTML = `<table><thead><tr><th data-column-start="0">Name</th><th data-column-start="1">Value</th></tr></thead>
    <tbody><tr><td colspan="2">Closed group</td></tr></tbody></table>`;
  scroller.querySelector("table").getBoundingClientRect = () => ({left: 10});
  const [name, value] = scroller.querySelectorAll("th");
  name.getBoundingClientRect = () => ({left: 10});
  value.getBoundingClientRect = () => ({left: 80});
  const viewport = new TableViewport({scroller, getOptions: () => ({freeze_columns: 2})});
  viewport.applyFrozenOffsets();
  assert.equal(name.style.left, "0px");
  assert.equal(value.style.left, "70px");
  viewport.destroy();
});

test("spanning group labels freeze at their styled indentation without changing column spans", () => {
  const scroller = dom.window.document.createElement("div");
  scroller.innerHTML = `<table><tbody>
    <tr><td class="et-display-heading" colspan="2" style="padding-left:20px"><span class="et-display-label">North</span></td></tr>
    <tr><td class="et-display-heading et-display-align-center" colspan="2"><span class="et-display-label">Centered</span></td></tr>
    <tr><td data-column-index="0">A</td><td data-column-index="1">10</td></tr>
    </tbody></table>`;
  const options = {freeze_columns: 1};
  const viewport = new TableViewport({scroller, getOptions: () => options});
  const [label, centered] = scroller.querySelectorAll(".et-display-label");
  viewport.applyFrozenOffsets();
  assert.ok(label.classList.contains("et-frozen-heading-label"));
  assert.equal(label.style.left, "20px");
  assert.equal(label.parentElement.colSpan, 2);
  assert.equal(label.parentElement.style.position, "");
  assert.ok(!centered.classList.contains("et-frozen-heading-label"));
  options.freeze_columns = 0;
  viewport.applyFrozenOffsets();
  assert.ok(!label.classList.contains("et-frozen-heading-label"));
  assert.equal(label.style.left, "");
  assert.equal(scroller.querySelector("[data-column-index='0']").style.position, "");
  const ordinary = scroller.querySelector("[data-column-index='1']");
  ordinary.style.position = "relative";
  ordinary.style.left = "3px";
  viewport.applyFrozenOffsets();
  assert.equal(ordinary.style.position, "relative", "unfrozen cell styles belong to their renderer");
  assert.equal(ordinary.style.left, "3px");
  viewport.destroy();
});

test("spanning headings measure a frozen boundary from physical cells and clear it when unfrozen", () => {
  const scroller = dom.window.document.createElement("div");
  scroller.innerHTML = `<table><thead><tr>
    <th data-column-start="0">Name</th><th data-column-start="1">Value</th></tr></thead><tbody>
    <tr><td class="et-display-heading" colspan="2" style="padding:4px 6px 5px 20px">
    <span class="et-display-label">North</span></td></tr></tbody></table>`;
  scroller.querySelector("table").getBoundingClientRect = () => ({left: 10});
  let widths = [90, 140];
  for (const [index, cell] of [...scroller.querySelectorAll("th")].entries()) {
    cell.getBoundingClientRect = () => ({left: 10 + (index ? widths[0] : 0),
      right: 10 + widths[0] + (index ? widths[1] : 0)});
  }
  const options = {freeze_columns: 1};
  const viewport = new TableViewport({scroller, getOptions: () => options});
  const label = scroller.querySelector(".et-display-label");
  viewport.applyFrozenOffsets();
  assert.equal(label.style.getPropertyValue("--et-heading-frozen-width"), "90px");
  assert.equal(label.style.getPropertyValue("--et-heading-frozen-left"), "20px");
  assert.equal(label.style.getPropertyValue("--et-heading-frozen-top"), "4px");
  assert.equal(label.style.getPropertyValue("--et-heading-frozen-bottom"), "5px");
  options.freeze_columns = 2;
  viewport.applyFrozenOffsets();
  assert.equal(label.style.getPropertyValue("--et-heading-frozen-width"), "230px");
  widths = [100, 160];
  viewport.applyFrozenOffsets();
  assert.equal(label.style.getPropertyValue("--et-heading-frozen-width"), "260px");
  options.freeze_columns = 0;
  viewport.applyFrozenOffsets();
  assert.equal(label.style.getPropertyValue("--et-heading-frozen-width"), "");
  assert.ok(!label.classList.contains("et-frozen-heading-label"));
  assert.equal(label.parentElement.colSpan, 2);
  viewport.destroy();
});

test("freezing keeps header and footer axes aligned with their physical columns", () => {
  const scroller = dom.window.document.createElement("div");
  scroller.innerHTML = `<table><thead>
    <tr><th data-column-start="0" rowspan="2">Country</th><th data-column-start="1">Value</th></tr>
    <tr class="et-axis-row"><td data-column-index="1">Top axis</td></tr>
    </thead><tbody><tr><td data-column-index="0">A</td><td data-column-index="1">4</td></tr></tbody>
    <tfoot><tr><td data-column-index="0"></td><td data-column-index="1">Bottom axis</td></tr></tfoot></table>`;
  scroller.querySelector("table").getBoundingClientRect = () => ({left: 10});
  scroller.querySelector("thead tr").getBoundingClientRect = () => ({height: 25});
  for (const cell of scroller.querySelectorAll("tbody td")) {
    cell.getBoundingClientRect = () => ({left: Number(cell.dataset.columnIndex) === 0 ? 10 : 100});
  }
  const viewport = new TableViewport({scroller, getOptions: () => ({freeze_columns: 2})});
  viewport.applyFrozenOffsets();
  const top = scroller.querySelector("thead td");
  const bottom = scroller.querySelector('tfoot td[data-column-index="1"]');
  assert.equal(top.style.left, "90px");
  assert.equal(top.style.top, "25px");
  assert.equal(bottom.style.left, "90px");
  assert.equal(top.style.position, "sticky");
  assert.equal(bottom.style.position, "sticky");
  assert.ok(Number(top.style.zIndex) > Number(bottom.style.zIndex));
  viewport.destroy();
});

test("fullscreen pagination reserves space for a bottom scale outside the body", () => {
  const scroller = dom.window.document.createElement("div");
  scroller.innerHTML = '<table><thead></thead><tbody><tr><td>A</td></tr></tbody><tfoot></tfoot></table>';
  Object.defineProperty(scroller, "clientHeight", {value: 100});
  let size = 10, renders = 0, projection = {};
  scroller.querySelector("tbody").getBoundingClientRect = () => ({height: size * 20});
  scroller.querySelector("table").getBoundingClientRect = () => ({height: 40 + size * 20});
  const viewport = new TableViewport({scroller, getOptions: () => ({}),
    getPageSizeOverride: () => size, setPageSizeOverride: value => { size = value; },
    getPageMetrics: () => ({count: size, remaining: 100, projection}), rerender() { renders++; }});
  viewport.expanded = true;
  viewport.fit();
  assert.equal(size, 2);
  const fitted = renders;
  viewport.fit();
  assert.equal(renders, fitted, "unchanged geometry must not repeatedly probe an overflowing extra row");
  projection = {};
  viewport.fit();
  assert.ok(renders > fitted, "a new dataset must be measured even when its initial geometry matches");
  viewport.destroy();
});

test("fullscreen measures the entire body including tall rows and display annotations", () => {
  const scroller = dom.window.document.createElement("div");
  scroller.innerHTML = '<table><thead></thead><tbody></tbody></table>';
  Object.defineProperty(scroller, "clientHeight", {value: 200});
  let size = 10;
  // 40px header, 60px section/summary chrome, one 10px row then 40px rows.
  const bodyHeight = () => 60 + 10 + (size - 1) * 40;
  scroller.querySelector("tbody").getBoundingClientRect = () => ({height: bodyHeight()});
  scroller.querySelector("table").getBoundingClientRect = () => ({height: 40 + bodyHeight()});
  const viewport = new TableViewport({scroller, getOptions: () => ({}),
    getPageSizeOverride: () => size, setPageSizeOverride: value => {size = value;},
    getPageMetrics: () => ({count: size, remaining: 100}), rerender() {}});
  viewport.expanded = true;
  viewport.fit();
  assert.equal(size, 3);
  assert.ok(40 + bodyHeight() <= 200);
  assert.ok(40 + bodyHeight() + 40 > 200);
  viewport.destroy();
});

test("viewport observes and releases the current table as well as its available space", t => {
  const observed = [], released = [];
  t.mock.method(global.ResizeObserver.prototype, "observe", el => observed.push(el));
  t.mock.method(global.ResizeObserver.prototype, "unobserve", el => released.push(el));
  const root = dom.window.document.createElement("div"), scroller = root.appendChild(dom.window.document.createElement("div"));
  const first = dom.window.document.createElement("table"), second = dom.window.document.createElement("table");
  const viewport = new TableViewport({root, scroller, getOptions: () => ({})});
  viewport.observeTable(first);
  viewport.observeTable(first);
  viewport.observeTable(second);
  assert.deepEqual(observed, [scroller, root, first, second]);
  assert.deepEqual(released, [first]);
  viewport.destroy();
});

test("a single oversized record stays accessible instead of fitting an empty page", () => {
  const scroller = dom.window.document.createElement("div");
  scroller.innerHTML = '<table><tbody></tbody></table>';
  Object.defineProperty(scroller, "clientHeight", {value: 200});
  let size = 10;
  scroller.querySelector("tbody").getBoundingClientRect = () => ({height: size * 500});
  scroller.querySelector("table").getBoundingClientRect = () => ({height: 40 + size * 500});
  const viewport = new TableViewport({scroller, getOptions: () => ({}),
    getPageSizeOverride: () => size, setPageSizeOverride: value => {size = value;},
    getPageMetrics: () => ({count: size, remaining: 100}), rerender() {}});
  viewport.expanded = true;
  viewport.fit();
  assert.equal(size, 1);
  viewport.destroy();
});
