import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import { formatValue } from "./src/format.js";
import { formattedText } from "./src/formatted-text.js";
import { renderSparkline } from "./src/sparkline.js";
import { EvidentialTableRenderer } from "./src/table.js";

const dom = new JSDOM("<!doctype html><body></body>", {pretendToBeVisual: true});
global.window = dom.window;
global.document = dom.window.document;
global.Node = dom.window.Node;
global.HTMLElement = dom.window.HTMLElement;
global.ResizeObserver = class { observe() {} disconnect() {} };
global.requestAnimationFrame = cb => setTimeout(cb, 0);
global.cancelAnimationFrame = clearTimeout;

test("sci uses a multiplication sign and normalized raised exponents", () => {
  for (const [value, expected] of [
    [123456, "1.23 × 10⁵"], [0.000123, "1.23 × 10⁻⁴"], [-123456, "-1.23 × 10⁵"],
    [0, "0.00 × 10⁰"], [1, "1.00 × 10⁰"], [9.999, "1.00 × 10¹"],
    [1e-300, "1.00 × 10⁻³⁰⁰"], [Number.MIN_VALUE, "4.94 × 10⁻³²⁴"],
    [Number.MAX_VALUE, "1.80 × 10³⁰⁸"], ["123456", "1.23 × 10⁵"],
  ]) assert.equal(formatValue(value, "sci"), expected);
  assert.equal(formatValue(null, "sci"), "–");
  assert.equal(formatValue("Unavailable", "sci", {type: "number"}), "Unavailable");
  assert.equal(formatValue(NaN, "sci", {fallback: "Missing"}), "Missing");
  assert.equal(formatValue(123456, "0.000E+0"), "1.235E+5");
});

test("scientific HTML uses real sup elements, preserves surrounding text and escapes markup", () => {
  const target = document.createElement("span");
  target.append(formattedText("<img src=x onerror=alert(1)> (1.23 × 10⁻⁴) to 2.00 × 10⁵ units"));
  assert.deepEqual([...target.querySelectorAll("sup")].map(node => node.textContent), ["-4", "5"]);
  assert.equal(target.querySelector("img"), null);
  assert.equal(target.querySelector("[role=math]").getAttribute("aria-label"), "1.23 times 10 to the power of -4");
  assert.ok(target.textContent.startsWith("<img src=x onerror=alert(1)> ("));
  assert.ok(target.textContent.endsWith(" units"));
  assert.equal(formattedText("ordinary <b>text</b>"), "ordinary <b>text</b>");
});

test("cells, chips, templates, mark labels, stack labels, statistics and axes share scientific HTML", () => {
  const el = document.createElement("div");
  document.body.append(el);
  const rows = [{plain: 123456, chip: 0.000123, bar: 123456, stack: 123456, negative: -123456}];
  const columns = [
    {name: "plain", type: "number", fmt: "sci"},
    {name: "chip", type: "number", fmt: "sci", viz: "chip"},
    {name: "bar", type: "number", fmt: "sci", encodings: [{kind: "bar", source: "bar", label: {value: true}}], scale: {domain: [0, 200000], axis: true}},
    {name: "stack", type: "number", fmt: "sci", encodings: [{kind: "stacked_bar", source: "stack", label: {value: true}}]},
    {name: "negative", type: "number", fmt: "sci", bracket_negatives: true},
    {name: "template", template: "Total: {plain}", template_fmt: {plain: "sci"}},
  ];
  const data = {rows, columns, options: {column_stats: true}};
  const renderer = new EvidentialTableRenderer({get: key => data[key], on() {}, off() {}}, el);
  const cells = el.querySelectorAll("tbody td");
  for (const cell of cells) assert.ok(cell.querySelector("sup.et-scientific-exponent"), cell.outerHTML);
  assert.equal(cells[1].querySelector("sup").textContent, "-4");
  assert.equal(cells[2].querySelector(".et-mark-label").title, "1.23 × 10⁵");
  assert.match(cells[4].textContent, /^\(1\.23 × 10/);
  assert.ok(el.querySelector(".et-stats-value sup"));
  assert.ok(el.querySelector(".et-axis-tick sup"));
  renderer.destroy();
  el.remove();
});

test("SVG tooltips use readable text without HTML tags", () => {
  const chart = renderSparkline({sparkline_options: {type: "points", y_fmt: "sci"}}, [123456]);
  const title = chart.querySelector("title");
  assert.equal(title.textContent, "0: 1.23 × 10⁵");
  assert.equal(title.querySelector("sup"), null);
});
