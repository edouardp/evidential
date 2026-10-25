import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import { sparklinePoints } from "./src/sparkline-data.js";
import { renderSparkline } from "./src/sparkline.js";
import { prepareChangeScales } from "./src/change-sparkline.js";
import { RowPipeline } from "./src/derived.js";

const dom = new JSDOM("<!doctype html>");
global.document = dom.window.document;
global.Node = dom.window.Node;
const options = {type: "change", delta: true};
const changes = (series, opts = options) => sparklinePoints(series, opts).map(point => point[1]);
const render = (series, opts = options) => renderSparkline({sparkline_options: opts}, series);

test("adjacent differences show decreases in positive absolute measurements", () => {
  const source = Object.freeze([3, 5, 4, 7, 9, 8, 11, 13]);
  assert.deepEqual(changes(source), [null, 2, -1, 3, 2, -1, 3, 2]);
  const svg = render(source, {...options, width: 80, y_fmt: "num1"});
  const marks = [...svg.querySelectorAll("rect")];
  assert.deepEqual(marks.map(mark => mark.dataset.state), ["up", "down", "up", "up", "down", "up", "up"]);
  assert.equal(Number(marks[0].getAttribute("x")), 11.5);
  assert.equal(marks[1].textContent, "2: -1.0 (down)");
  assert.match(svg.getAttribute("aria-label"), /5 up, 0 steady, 2 down, 1 missing/);
  for (const opts of [{type: "change"}, {type: "change", delta: false}]) {
    assert.deepEqual([...render([5, 4], opts).querySelectorAll("rect")].map(mark => mark.dataset.state), ["up", "up"]);
  }
});

test("missing and invalid observations break comparisons without bridging gaps", () => {
  assert.deepEqual(changes([1, 2, null, 5, 4, NaN, 10, 11]), [null, 1, null, null, -1, null, null, 1]);
  assert.deepEqual(changes([1, "bad", 3, 4]), [null, null, null, 1]);
  assert.deepEqual(changes([1e308, -1e308, -1e308]), [null, null, 0]);
  for (const series of [[], [5], [null, 5], [1, null, 3]]) assert.equal(render(series).textContent, "–");
});

test("structured and pair inputs preserve original observations and x bindings", () => {
  const series = Object.freeze([
    Object.freeze({period: "Jan", revenue: 5}), Object.freeze({period: "Mar", revenue: 4}),
    Object.freeze({period: "Apr", revenue: 4}),
  ]);
  const points = sparklinePoints(series, {...options, x: "period", y: "revenue"});
  assert.deepEqual(points.map(([x, y]) => [x, y]), [["Jan", null], ["Mar", -1], ["Apr", 0]]);
  assert.equal(points[1][2], series[1]);
  assert.deepEqual(changes([[1, 5], [10, 4], [20, 8]]), [null, -1, 4]);
});

test("steady thresholds and inferred gradients use differences rather than absolute levels", () => {
  const opts = {...options, steady: [-1, 1], color_scale: ["red", "gray", "blue"]};
  const column = {name: "series", viz: "sparkline", sparkline_options: opts};
  const rows = [{series: [100, 104, 103]}, {series: [1000, 996, 997]}];
  const scale = prepareChangeScales([column], rows).get(column);
  assert.equal(scale(-4), "#ff0000");
  assert.equal(scale(4), "#0000ff");
  const marks = [...renderSparkline(column, rows[0].series, scale).querySelectorAll("rect")];
  assert.deepEqual(marks.map(mark => mark.dataset.state), ["up", "steady"]);
  assert.deepEqual(marks.map(mark => mark.getAttribute("fill")), ["#0000ff", "#808080"]);
});

test("shared domains pool computed differences consistently with rendered change colors", () => {
  const column = {name: "series", viz: "sparkline", domain: {name: "change", palette: ["red", "gray", "blue"]},
    sparkline_options: options};
  const rows = [{series: [100, 103, 101]}, {series: [1000, 1001]}];
  const prepared = new RowPipeline().get({rows, columns: [column], options: {}, search: "", hidden: new Set(), sort: null});
  assert.deepEqual(prepared.ranges.get(column), {min: -2, max: 3, shared: true});
  const scale = prepared.changeScales.get(column);
  const marks = [...renderSparkline(column, rows[0].series, scale).querySelectorAll("rect")];
  assert.deepEqual(marks.map(mark => mark.getAttribute("fill")), [scale(3), scale(-2)]);
});
