import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import widget, { windowRange } from "./src/dimension-grid.js";

function mount({ count = 230, multiple = false } = {}) {
  const dom = new JSDOM("<!doctype html><body><main></main>", { pretendToBeVisual: true });
  global.window = dom.window;
  global.document = dom.window.document;
  global.Node = dom.window.Node;
  const listeners = new Map();
  const state = {
    options: { format: "num0", height: 280, dimension_width: 220, color: "#93b4ef", multiple },
    facets: [{ name: "service", items: Array.from({ length: count }, (_, index) => ({ value: `Service ${index}`, metric: count - index })) }],
    selected: {},
  };
  let saves = 0;
  const model = {
    get: name => state[name],
    set(name, value) { state[name] = value; for (const listener of listeners.get(`change:${name}`) || []) listener(); },
    on(name, listener) { if (!listeners.has(name)) listeners.set(name, new Set()); listeners.get(name).add(listener); },
    off(name, listener) { listeners.get(name)?.delete(listener); },
    save_changes() { saves++; },
  };
  const el = document.querySelector("main");
  const cleanup = widget.render({ model, el });
  return { dom, el, model, state, cleanup, listeners, saves: () => saves };
}

function searchFor(value) {
  document.querySelector(".edg-search-toggle").click();
  const input = document.querySelector("input");
  input.value = value;
  input.dispatchEvent(new window.Event("input"));
  return input;
}

test("search covers low-ranked categories and retains its indicator on blur", () => {
  const { el, cleanup } = mount();
  assert.ok(el.querySelectorAll(".edg-row").length < 30);
  const input = searchFor("service 229");
  assert.equal(el.querySelectorAll(".edg-row").length, 1);
  assert.equal(el.querySelector(".edg-category").textContent, "Service 229");
  input.blur();
  assert.equal(input.hidden, true);
  assert.equal(el.querySelector(".edg-heading").hidden, false);
  assert.equal(el.querySelector(".edg-search-toggle").classList.contains("edg-filtered"), true);
  assert.match(el.querySelector(".edg-search-toggle").getAttribute("aria-label"), /service 229/);
  cleanup();
});

test("x clears a search, selections remain visible through nonmatching searches", () => {
  const { el, state, saves, cleanup } = mount();
  el.querySelector(".edg-row").click();
  assert.deepEqual(state.selected, { service: ["Service 0"] });
  searchFor("service 229");
  assert.equal(el.querySelector(".edg-pinned .edg-category").textContent, "Service 0");
  el.querySelector(".edg-search-toggle").click();
  assert.equal(el.querySelector("input").value, "");
  assert.match(el.querySelector(".edg-status").textContent, /229 available/);
  el.querySelector(".edg-pinned .edg-row").click();
  assert.deepEqual(state.selected, {});
  assert.equal(saves(), 2);
  cleanup();
});

test("single selections replace and multiple selections accumulate; reset clears", () => {
  for (const multiple of [false, true]) {
    const { el, state, cleanup } = mount({ multiple });
    el.querySelector(".edg-list .edg-row").click();
    el.querySelector(".edg-list .edg-row").click();
    assert.deepEqual(state.selected.service, multiple ? ["Service 0", "Service 1"] : ["Service 1"]);
    el.querySelector(".edg-reset").click();
    assert.deepEqual(state.selected, {});
    cleanup();
  }
});

test("scrolling windows far down the dimension without growing the DOM", () => {
  const { el, cleanup } = mount({ count: 10000 });
  const list = el.querySelector(".edg-list");
  list.scrollTop = 28 * 9000;
  list.dispatchEvent(new window.Event("scroll"));
  assert.ok(el.querySelectorAll(".edg-row").length < 30);
  assert.match(el.querySelector(".edg-category").textContent, /Service 8996/);
  assert.deepEqual(windowRange(10, 0, 280), [0, 10]);
  cleanup();
});

test("search and scroll survive backend facet updates; listeners clean up", () => {
  const { el, model, state, cleanup, listeners } = mount();
  const input = searchFor("229");
  model.set("facets", [{ ...state.facets[0], items: [{ value: "Service 229", metric: 999 }] }]);
  assert.equal(document.activeElement, input);
  assert.equal(input.value, "229");
  assert.equal(el.querySelector(".edg-value").textContent, "999");
  cleanup();
  assert.equal(el.children.length, 0);
  assert.ok([...listeners.values()].every(set => set.size === 0));
});

test("category names are text, not HTML", () => {
  const { el, model, cleanup } = mount();
  model.set("facets", [{ name: "service", items: [{ value: "<img src=x onerror=alert(1)>", metric: 1 }] }]);
  assert.equal(el.querySelector("img"), null);
  assert.match(el.querySelector(".edg-category").textContent, /<img/);
  cleanup();
});
