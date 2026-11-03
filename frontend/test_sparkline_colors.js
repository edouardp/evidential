import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import { renderSparkline, sparklinePoints } from "./src/sparkline.js";
import { sparklineColorScale, prepareSparklineScales } from "./src/sparkline-colors.js";
import { inspectionData } from "./src/tooltips.js";
import { RowPipeline } from "./src/derived.js";
import { buildColorVizScale, calculateColorStyles, getColorForValue } from "./src/color.js";

const dom = new JSDOM("<!doctype html><body></body>");
global.document = dom.window.document;
global.Node = dom.window.Node;
const colors = {color_scale: ["#ff0000", "#808080", "#0000ff"], min: -4, max: 8, midpoint: 0};
const column = (type, overrides = {}) => ({name: "series", viz: "sparkline", type: "array",
  sparkline_options: {type, width: 100, height: 30}, color_options: colors, ...overrides});
const values = [-4, 0, 8];

test("bars and points look up their own y, including explicit observation color overrides and tooltip swatches", () => {
  for (const type of ["bar", "points", "change"]) {
    const col = column(type);
    const source = [{x: 200, y: -4}, {x: 400, y: 0, color: "tab:green"}, {x: 1000, y: 8}];
    const svg = renderSparkline(col, source);
    const selector = type === "points" ? "circle" : "rect";
    const marks = [...svg.querySelectorAll(selector)];
    assert.deepEqual(marks.map(mark => mark.getAttribute("fill")), ["#ff0000", "#2ca02c", "#0000ff"]);
    assert.deepEqual(marks.map(mark => inspectionData(mark).color), ["#ff0000", "#2ca02c", "#0000ff"]);
    assert.equal(source[1].color, "tab:green");
  }
});

test("line intervals and area fills take the starting observation's color without bridging missing values", () => {
  for (const type of ["line", "area"]) {
    const col = column(type);
    const source = [{x: 0, y: -4}, {x: 10, y: 0, color: "tab:green"}, {x: 20, y: 8},
      {x: 30, y: null}, {x: 40, y: 8}, {x: 50, y: 0}];
    const svg = renderSparkline(col, source);
    const lines = [...svg.querySelectorAll("polyline")];
    assert.deepEqual(lines.map(line => line.getAttribute("stroke")), ["#ff0000", "#2ca02c", "#0000ff"]);
    assert.ok(lines.every(line => line.getAttribute("points").split(" ").length === 2));
    assert.equal(svg.querySelectorAll("polygon").length, type === "area" ? 3 : 0);
    if (type === "area") {
      assert.deepEqual([...svg.querySelectorAll("polygon")].map(area => area.getAttribute("fill")),
        ["#ff0000", "#2ca02c", "#0000ff"]);
      assert.ok([...svg.querySelectorAll("polygon")].every(area => area.getAttribute("opacity") === "0.22"));
    }
    assert.doesNotMatch(svg.outerHTML, /NaN|Infinity/);
  }
});

test("per-observation colors also work without a gradient, and do not become x labels", () => {
  const source = [{y: 1, color: "red"}, {y: 2, color: "blue"}, {y: 3, color: "green"}];
  assert.deepEqual(sparklinePoints(source, {}).map(([x]) => x), [0, 1, 2]);
  for (const type of ["bar", "points", "change", "line", "area"]) {
    const svg = renderSparkline(column(type, {color_options: {}}), source);
    const marks = [...svg.querySelectorAll(type === "points" ? "circle" : ["line", "area"].includes(type) ? "polyline" : "rect")];
    assert.equal(marks[0].getAttribute(["line", "area"].includes(type) ? "stroke" : "fill"), "red");
    assert.equal(marks[1].getAttribute(["line", "area"].includes(type) ? "stroke" : "fill"), "blue");
  }
});

test("gradient lookup matches scalar color encodings, including midpoint, stops, clamping, and alpha", () => {
  for (const config of [colors, {color_scale: "viridis", min: -4, max: 8}, {
    color_stops: [{value: -4, color: "#ff0000"}, {value: 0, color: "#ffffffcc"}, {value: 8, color: "#0000ff"}],
  }]) {
    const col = column("line", {color_options: config});
    const scalar = buildColorVizScale({color_options: config}, {min: -4, max: 8});
    const lookup = sparklineColorScale(col, values);
    for (const y of [-100, -4, -2, 0, 4, 8, 100]) assert.equal(lookup(y), getColorForValue(y, scalar));
  }
  const constant = sparklineColorScale(column("bar", {color_options: {color_scale: ["red", "blue"]}}), [5, 5]);
  assert.notEqual(constant(5), "#ff0000");
  assert.notEqual(constant(5), "#0000ff");
});

test("auto bounds pool matching rows per physical column and are cached across page changes", () => {
  const a = column("bar", {color_options: {color_scale: ["red", "blue"]}});
  const b = column("points", {color_options: {color_scale: ["red", "blue"], min: -1, max: 1}});
  const rows = [{name: "Keep", series: [-2, 1]}, {name: "Other", series: [2, 8]},
    {render_type: "row_total", series: [-1000, 1000]}];
  const scales = prepareSparklineScales([a, b], rows);
  assert.equal(scales.get(a)(-2), "#ff0000");
  assert.equal(scales.get(a)(8), "#0000ff");
  assert.notEqual(scales.get(a)(1), scales.get(b)(1));
  const pipeline = new RowPipeline();
  const args = {rows: rows.slice(0, 2), columns: [{name: "name"}, a], options: {page_size: 1}, search: "", hidden: new Set(), sort: null};
  const prepared = pipeline.get(args);
  assert.equal(prepared.sparklineScales.get(a)(1), scales.get(a)(1));
  assert.equal(pipeline.get(args).sparklineScales, prepared.sparklineScales);
  const filtered = pipeline.get({...args, search: "Keep"});
  assert.equal(filtered.sparklineScales.get(a)(1), "#0000ff");
  // Standalone rendering and the pipeline agree when given the same observed domain.
  const standalone = sparklineColorScale(a, [-2, 8]);
  assert.equal(standalone(1), prepared.sparklineScales.get(a)(1));
});

test("shared domains reuse a scalar palette and inferred bounds even with hidden members", () => {
  const domain = {name: "readings", bounds: [-4, 8], palette: colors.color_scale, midpoint: 0};
  const spark = column("area", {domain, color_options: {}});
  const scalar = {name: "value", viz: "color", type: "number", domain};
  const rows = [{series: [-4, 0, 8], value: 0}];
  const prepared = new RowPipeline().get({rows, columns: [spark, scalar], options: {}, search: "", hidden: new Set(["value"]), sort: null});
  const lookup = prepared.sparklineScales.get(spark);
  const scalarScale = buildColorVizScale(scalar, prepared.ranges.get(scalar));
  for (const y of values) assert.equal(lookup(y), getColorForValue(y, scalarScale));
});

test("marker overrides and signed area defaults retain their precedence while gradients use y values", () => {
  const col = column("area", {sparkline_options: {type: "area", signed: true, markers: true, marker_color: "black"}});
  const svg = renderSparkline(col, values);
  assert.deepEqual([...svg.querySelectorAll("polygon")].map(area => area.getAttribute("fill")), ["#ff0000", "#808080"]);
  assert.ok([...svg.querySelectorAll("circle")].every(dot => dot.getAttribute("fill") === "black"));
  const plain = renderSparkline({...col, color_options: {}, sparkline_options: {type: "area", signed: true}}, values);
  assert.equal(plain.querySelectorAll("polygon").length, 2);
  assert.match(plain.querySelectorAll("polygon")[1].getAttribute("fill"), /--et-negative/);
});

test("a constant shared domain gives sparkline observations and scalar heatmaps the same color", () => {
  const domain = {name: "constant", palette: "viridis"};
  const spark = column("points", {domain, color_options: {}});
  const scalar = {name: "value", viz: "color", type: "number", domain};
  const rows = [{series: [5, 5], value: 5}];
  const result = new RowPipeline().get({rows, columns: [spark, scalar], options: {}, search: "", hidden: new Set(), sort: null});
  const scale = result.colorScales.get(scalar);
  const cellColor = calculateColorStyles(scalar, rows[0], result.ranges.get(scalar), scale).backgroundColor;
  assert.equal(result.sparklineScales.get(spark)(5), cellColor);
});

test("gradient bounds affect only color, not bar geometry or the explicit reference origin", () => {
  const col = column("bar", {sparkline_options: {type: "bar", reference: 1, width: 100, height: 30}});
  const attributes = svg => [...svg.querySelectorAll("rect")].map(rect =>
    ["x", "y", "width", "height"].map(name => rect.getAttribute(name)));
  assert.deepEqual(attributes(renderSparkline(col, [-10, 0, 20])),
    attributes(renderSparkline({...col, color_options: {}}, [-10, 0, 20])));
});
