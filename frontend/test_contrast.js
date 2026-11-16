import {test} from "node:test";
import assert from "node:assert/strict";
import {JSDOM} from "jsdom";
import {autoContrast, clearAutoContrast, paintResolver, refreshContrast, ContrastController} from "./src/contrast.js";

function fixture() {
  const dom = new JSDOM('<body style="background:white"><div id="host"><div id="root"><table><tbody><tr><td class="et-td">4%</td></tr></tbody></table></div></div></body>');
  const document = dom.window.document;
  return {view: dom.window, document, host: document.querySelector("#host"),
    root: document.querySelector("#root"), cell: document.querySelector("td")};
}

test("paint resolution follows the CSS cell layer order and caches shared ancestor reads", () => {
  const {view, root, cell} = fixture();
  cell.style.setProperty("--et-row-tint", "rgba(0,0,0,0.5)");
  cell.style.setProperty("--et-cell-fill", "rgba(220,38,38,0.22)");
  cell.style.setProperty("--et-selection-tint", "rgba(0,0,255,0.2)");
  let reads = 0;
  const original = view.getComputedStyle.bind(view);
  view.getComputedStyle = node => { reads++; return original(node); };
  const paint = paintResolver(root);
  const rgb = paint.background(cell).rgb();
  for (const [index, value] of [119, 87, 138].entries()) assert.ok(Math.abs(rgb[index] - value) <= 1);
  const first = reads;
  assert.equal(paint.background(cell), paint.background(cell));
  assert.equal(reads, first);
  assert.equal(paint.color("invalid paint").alpha(), 0);
  paint.destroy();
  assert.equal(root.querySelector(":scope > span"), null);
});

test("native system and modern CSS colours resolve through the browser with graceful fallbacks", () => {
  const {view, document, root} = fixture();
  const original = view.getComputedStyle.bind(view);
  view.getComputedStyle = node => node.tagName === "SPAN" ? {backgroundColor: "rgb(17, 24, 39)"} : original(node);
  let paint = paintResolver(root);
  assert.equal(paint.color("Canvas").hex(), "#111827");
  paint.destroy();

  // Native computed colour spaces are rasterized once per distinct colour.
  view.CanvasRenderingContext2D = class {};
  view.getComputedStyle = node => node.tagName === "SPAN" ? {backgroundColor: "color(srgb 0.1 0.2 0.3)"} : original(node);
  const create = document.createElement.bind(document);
  let samples = 0;
  document.createElement = tag => tag !== "canvas" ? create(tag) : {getContext: () => ({
    clearRect() {}, fillRect() {}, getImageData() { samples++; return {data: [17, 24, 39, 255]}; },
  })};
  paint = paintResolver(root);
  assert.equal(paint.color("Canvas").hex(), "#111827");
  assert.equal(paint.color("Canvas").hex(), "#111827");
  assert.equal(samples, 1);
  paint.destroy();
  document.createElement = tag => tag !== "canvas" ? create(tag) : {getContext: () => null};
  paint = paintResolver(root);
  assert.equal(paint.color("Canvas").alpha(), 0);
  paint.destroy();
});

test("auto contrast uses row, chip, mark opacity and full-track underlays; clearing restores explicit control", () => {
  const {root, cell, document} = fixture();
  cell.style.setProperty("--et-cell-fill", "rgba(220,38,38,0.22)");
  autoContrast(cell, {policy: "cell"});
  refreshContrast(root);
  assert.equal(cell.style.color, "rgb(0, 0, 0)");
  cell.style.backgroundColor = "#111827";
  refreshContrast(root);
  assert.equal(cell.style.color, "rgb(255, 255, 255)");
  clearAutoContrast(cell);
  cell.style.color = "purple";
  refreshContrast(root);
  assert.equal(cell.style.color, "purple");

  const track = document.createElement("div"); track.className = "et-marks";
  const underlay = document.createElement("div"); underlay.className = "et-mark-background";
  underlay.style.backgroundColor = "white"; track.append(underlay);
  const mark = document.createElement("div"); mark.style.opacity = "0.55"; track.append(mark);
  const label = document.createElement("span"); track.append(label); cell.append(track);
  label.style.setProperty("--et-label-fill", "rgba(0,0,0,0.4)");
  autoContrast(label, {mark});
  refreshContrast(root);
  assert.equal(label.style.color, "rgb(0, 0, 0)");
  underlay.remove();
  refreshContrast(root);
  assert.equal(label.style.color, "rgb(255, 255, 255)");
  const chip = document.createElement("span"); chip.style.backgroundColor = "rgba(255,255,255,0.1)";
  cell.append(chip); autoContrast(chip); refreshContrast(root);
  assert.equal(chip.style.color, "rgb(255, 255, 255)");
});

test("paint traversal crosses an anywidget shadow boundary", () => {
  const {host, document} = fixture();
  host.style.backgroundColor = "#111827";
  const shadow = host.attachShadow({mode: "open"});
  const root = document.createElement("div"), node = document.createElement("span");
  root.append(node); shadow.append(root); node.style.backgroundColor = "rgba(255,255,255,0.1)";
  autoContrast(node); refreshContrast(root);
  assert.equal(node.style.color, "rgb(255, 255, 255)");
});

test("theme observers coalesce changes, ignore their own text writes and clean up pending work", async () => {
  const {view, host, root, cell} = fixture();
  const frames = [], listeners = new Map();
  let removed = false;
  view.matchMedia = () => ({addEventListener: (name, fn) => listeners.set(name, fn),
    removeEventListener: (name, fn) => { removed = listeners.get(name) === fn; }});
  cell.style.setProperty("--et-cell-fill", "rgba(220,38,38,0.22)");
  autoContrast(cell, {policy: "cell"});
  const controller = new ContrastController(root, fn => frames.push(fn)); controller.watch();
  host.style.backgroundColor = "#111827";
  await Promise.resolve();
  controller.schedule();
  assert.equal(frames.length, 1);
  frames.shift()();
  assert.equal(cell.style.color, "rgb(255, 255, 255)");
  await Promise.resolve();
  assert.equal(frames.length, 0);
  cell.closest("tr").className = "et-row-shaded";
  await Promise.resolve();
  assert.equal(frames.length, 1);
  frames.shift()();
  root.dispatchEvent(new view.MouseEvent("pointerover", {bubbles: true}));
  assert.equal(frames.length, 0);
  cell.dispatchEvent(new view.MouseEvent("pointerover", {bubbles: true}));
  assert.equal(frames.length, 1);
  frames.shift()();
  cell.dispatchEvent(new view.MouseEvent("pointerout", {bubbles: true, relatedTarget: cell}));
  assert.equal(frames.length, 0);
  listeners.get("change")();
  assert.equal(frames.length, 1);
  controller.destroy();
  assert.equal(removed, true);
  frames.shift()();
  controller.schedule();
  assert.equal(frames.length, 0);
  host.style.backgroundColor = "white";
  cell.dispatchEvent(new view.MouseEvent("pointerover", {bubbles: true}));
  await Promise.resolve();
  assert.equal(frames.length, 0);
});
