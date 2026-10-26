import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import { renderSparkline } from "./src/sparkline.js";
import { applySharedDomains } from "./src/shared-domains.js";

global.document = new JSDOM("<!doctype html><body></body>").window.document;
global.Node = document.defaultView.Node;
const render = (values, options = {}, range) => renderSparkline({sparkline_options: {
  type: "area", signed: true, fit_to_data: true, reference: 1, y_fmt: "pct1",
  width: 100, height: 23, color: "green", ...options,
}}, values, null, range);
const points = polygon => polygon.getAttribute("points").trim().split(/\s+/).map(point => point.split(",").map(Number));

test("signed areas meet at exact reference crossings with positive and negative fills", () => {
  const svg = render([0.5, 1.5]);
  const reference = svg.querySelector(".et-sparkline-reference");
  assert.equal(reference.getAttribute("y1"), "11.5");
  assert.equal(reference.textContent, "100.0%");
  assert.equal(reference.getAttribute("stroke-dasharray"), "2 2");
  const [above, below] = svg.querySelectorAll("polygon");
  assert.equal(above.getAttribute("fill"), "green");
  assert.match(below.getAttribute("fill"), /--et-negative/);
  assert.ok(points(above).some(([x,y]) => x === 50 && y === 11.5));
  assert.ok(points(below).some(([x,y]) => x === 50 && y === 11.5));
  assert.ok(points(above).every(([,y]) => y <= 11.5));
  assert.ok(points(below).every(([,y]) => y >= 11.5));
  const zeroOrigin = render([-1, 1], {reference: undefined});
  for (const polygon of zeroOrigin.querySelectorAll("polygon")) {
    assert.ok(points(polygon).some(([x,y]) => x === 50 && y === 11.5));
  }
});

test("one-sided and constant series include the reference, without filling from zero", () => {
  for (const [values, baseline] of [[[1.2, 1.5], 21.5], [[0.4, 0.8], 1.5], [[1, 1], 21.5]]) {
    const svg = render(values, {reference_color: "navy"});
    const line = svg.querySelector("line");
    assert.equal(Number(line.getAttribute("y1")), baseline);
    assert.equal(line.getAttribute("stroke"), "navy");
    for (const polygon of svg.querySelectorAll("polygon")) {
      assert.ok(points(polygon).every(([,y]) => y >= 1.5 && y <= 21.5));
    }
  }
});

test("reference areas preserve gaps, original values and percentage tooltips", () => {
  const svg = render([0.8, 1.2, null, 0.7, 1.3]);
  assert.equal(svg.querySelectorAll("polygon").length, 4);
  assert.equal(svg.querySelectorAll("polyline").length, 2);
  assert.deepEqual([...svg.querySelectorAll("circle title")].map(title => title.textContent),
    ["0: 80.0%", "1: 120.0%", "3: 70.0%", "4: 130.0%"]);
  assert.equal(render([null, null]).textContent, "–");
  const clipped = render([1.2, 1.5], {}, {min: 1.1, max: 1.6, shared: true});
  assert.equal(clipped.querySelectorAll("line").length, 0);
  assert.ok(points(clipped.querySelector("polygon")).every(([,y]) => y >= 1.5 && y <= 21.5));
});

test("shared sparkline domains include references unless explicit bounds override them", () => {
  const column = {name: "values", viz: "sparkline", domain: "ratios", sparkline_options: {reference: 1}};
  const rows = [{values: [1.2, 1.5]}];
  const range = applySharedDomains([column], rows, new Map()).get(column);
  assert.equal(range.min, 1);
  assert.equal(range.max, 1.5);
  column.domain = {name: "ratios", bounds: [1.1, 2]};
  assert.equal(applySharedDomains([column], rows, new Map()).get(column).min, 1.1);
});
