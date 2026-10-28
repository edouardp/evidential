import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import { renderSparkline } from "./src/sparkline.js";
import { changeState, changeColorScale, prepareChangeScales } from "./src/change-sparkline.js";
import { RowPipeline } from "./src/derived.js";

global.document = new JSDOM("<!doctype html><body></body>").window.document;
global.Node = document.defaultView.Node;
const render = (values, options = {}) => renderSparkline({sparkline_options: {type: "change", ...options}}, values);
const rects = svg => [...svg.querySelectorAll("rect")];
const number = (rect, name) => Number(rect.getAttribute(name));

test("up, steady and down use equal rectangles offset by exactly half their height", () => {
  const svg = render([-100, -1, 0, 1, 100], {width: 100, height: 20});
  const marks = rects(svg);
  assert.deepEqual(marks.map(mark => mark.dataset.state), ["down", "down", "steady", "up", "up"]);
  const h = number(marks[0], "height");
  assert.ok(marks.every(mark => number(mark, "height") === h && number(mark, "width") === 14));
  assert.equal(number(marks[0], "y") - number(marks[2], "y"), h / 2);
  assert.equal(number(marks[2], "y") - number(marks[3], "y"), h / 2);
  for (const mark of marks) {
    assert.ok(number(mark, "x") >= 0 && number(mark, "x") + number(mark, "width") <= 100);
    assert.ok(number(mark, "y") >= 0 && number(mark, "y") + h <= 20);
  }
  assert.equal(svg.querySelectorAll("circle,polyline,polygon,line").length, 0);
  assert.equal(svg.getAttribute("role"), "img");
  assert.match(svg.getAttribute("aria-label"), /2 up, 1 steady, 2 down, 0 missing/);
});

test("steady endpoints are inclusive, asymmetric and independent of magnitude", () => {
  assert.deepEqual([-1, 1, 1.5, 2, 3].map(value => changeState(value, [1, 2])), ["down", "steady", "steady", "steady", "up"]);
  assert.deepEqual(rects(render([-1, 1, 1.5, 2, 3], {steady: [1, 2]})).map(mark => mark.dataset.state),
    ["down", "steady", "steady", "steady", "up"]);
});

test("missing and invalid values leave ordinal gaps; structured x values label events", () => {
  const svg = render([{period: "2026-01", delta: 3}, null, {period: "2026-08", delta: -2},
    {period: "2026-09", delta: "oops"}, {period: "2026-10", delta: 0}], {x: "period", y: "delta", width: 100, y_fmt: "num1"});
  const marks = rects(svg);
  assert.deepEqual(marks.map(mark => number(mark, "x")), [3, 43, 83]);
  assert.equal(marks[0].textContent, "2026-01: 3\nChange: up");
  assert.equal(marks[2].textContent, "2026-10: 0\nChange: steady");
  assert.match(svg.getAttribute("aria-label"), /2 missing/);
  assert.equal(rects(render([[0, -1], [10, 1]])).length, 2);
  for (const values of [[], [null, undefined, NaN, Infinity, "bad"]]) assert.equal(render(values).textContent, "–");
});

test("neutral is the gradient midpoint across the entire steady interval and any domain asymmetry", () => {
  const scale = changeColorScale({steady: [-1, 2], color_domain: [-3, 10], color_scale: ["#ff0000", "#808080", "#0000ff"]}, []);
  assert.equal(scale(-3), "#ff0000");
  assert.equal(scale(10), "#0000ff");
  for (const value of [-1, 0, 1, 2]) assert.equal(scale(value), "#808080");
  assert.equal(scale(-30), scale(-3));
  assert.equal(scale(100), scale(10));
  assert.notEqual(scale(-2), scale(-3));
  assert.notEqual(scale(6), scale(10));
  assert.equal(scale(-2), changeColorScale({color_domain: [-3, 3], color_scale: ["#ff0000", "#808080", "#0000ff"]}, [])(-1.5));
});

test("default colors distinguish states; a constant color applies to every mark", () => {
  const marks = rects(render([-1, 0, 1]));
  assert.match(marks[0].getAttribute("fill"), /--et-negative/);
  assert.equal(marks[1].getAttribute("fill"), "#b8bcc2");
  assert.match(marks[2].getAttribute("fill"), /--et-accent/);
  assert.ok(rects(render([-1, 0, 1], {color: "tab:blue"})).every(mark => mark.getAttribute("fill") === "#1f77b4"));
});

test("named and even-length palettes anchor at their interpolated midpoint, including one-sided data", () => {
  for (const palette of ["RdBu", ["red", "blue"]]) {
    const opts = {color_scale: palette};
    const neutral = changeColorScale(opts, [-8, 0, 1])(0);
    for (const values of [[0], [0, 2], [-2, 0], [-100, 0, 100]]) {
      assert.equal(changeColorScale(opts, values)(0), neutral);
    }
  }
  assert.equal(changeColorScale({color_scale: ["red", "gray", "blue"], color_domain: [0, 10]}, [])(-1), "#ff0000");
});

test("auto color bounds are shared across matching rows and independent physical columns", () => {
  const a = {name: "changes", viz: "sparkline", sparkline_options: {type: "change", color_scale: ["red", "gray", "blue"]}};
  const b = {...a, sparkline_options: {...a.sparkline_options, color_domain: [-1, 1]}};
  const rows = [{changes: [-2, 1]}, {changes: [2, 8]}, {render_type: "row_total", changes: [-1000, 1000]}];
  const scales = prepareChangeScales([a, b], rows);
  assert.equal(scales.get(a)(8), "#0000ff");
  assert.notEqual(scales.get(a)(1), scales.get(b)(1));
  const first = renderSparkline(a, rows[0].changes, scales.get(a));
  const second = renderSparkline(a, [1, 8], scales.get(a));
  assert.equal(rects(first)[1].getAttribute("fill"), rects(second)[0].getAttribute("fill"));
  const pipeline = new RowPipeline();
  const args = {rows, columns: [a], options: {page_size: 1}, search: "", hidden: new Set(), sort: null};
  const prepared = pipeline.get(args);
  assert.equal(prepared.changeScales.get(a)(8), "#0000ff");
  assert.equal(pipeline.get(args).changeScales, prepared.changeScales);
});

test("long sequences and tiny dimensions stay finite and each mark stays within its slot", () => {
  const svg = render(Array.from({length: 200}, (_, index) => index % 3 - 1), {width: 64, height: 1});
  const marks = rects(svg);
  assert.equal(marks.length, 200);
  for (let index = 0; index < marks.length - 1; index++) {
    assert.ok(number(marks[index], "x") + number(marks[index], "width") < number(marks[index + 1], "x"));
  }
  assert.doesNotMatch(svg.outerHTML, /NaN|Infinity/);
});
