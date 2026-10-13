import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import { HoldController } from "./src/interactions.js";
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
