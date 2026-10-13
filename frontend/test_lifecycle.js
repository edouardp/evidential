import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import { HoldController, holdInterval } from "./src/interactions.js";
import { LoadingController } from "./src/loading.js";
import { TableViewport } from "./src/viewport.js";

const dom = new JSDOM("<body></body>");
global.window = dom.window;
global.ResizeObserver = class { observe() {} disconnect() {} };

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
