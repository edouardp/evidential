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

test("continuous lines/areas use one vertical y gradient per run without bridging gaps", () => {
  for (const type of ["line", "area"]) {
    const col = column(type);
    const source = [{x: 0, y: -4}, {x: 10, y: 0, color: "tab:green"}, {x: 20, y: 8},
      {x: 30, y: null}, {x: 40, y: 8}, {x: 50, y: 0}];
    const svg = renderSparkline(col, source);
    const lines = [...svg.querySelectorAll("polyline")];
    assert.deepEqual(lines.map(line => line.getAttribute("points").split(" ").length), [3, 2]);
    assert.equal(lines[0].getAttribute("stroke"), lines[1].getAttribute("stroke"));
    assert.match(lines[0].getAttribute("stroke"), /^url\(#et-sparkline-gradient-/);
    const gradient = svg.querySelector("linearGradient");
    assert.equal(gradient.getAttribute("gradientUnits"), "userSpaceOnUse");
    assert.equal(gradient.getAttribute("y1"), "28.5");
    assert.equal(gradient.getAttribute("y2"), "1.5");
    assert.equal(gradient.firstElementChild.getAttribute("stop-color"), "#ff0000");
    assert.equal(gradient.lastElementChild.getAttribute("stop-color"), "#0000ff");
    const midpoint = [...gradient.children].find(stop => Number(stop.getAttribute("offset")) === 1 / 3);
    assert.equal(midpoint.getAttribute("stop-color"), "#808080");
    assert.equal(svg.querySelectorAll("polygon").length, type === "area" ? 2 : 0);
    if (type === "area") {
      const areas = [...svg.querySelectorAll("polygon")];
      assert.equal(areas[0].getAttribute("fill"), areas[1].getAttribute("fill"));
      assert.match(areas[0].getAttribute("fill"), /^url\(#/);
      assert.ok(areas.every(area => area.getAttribute("opacity") === "1"));
    }
    // No green outgoing interval or invisible green tooltip swatch.
    assert.equal(inspectionData(svg.querySelectorAll("circle")[1]).color, "#808080");
    assert.doesNotMatch(svg.outerHTML, /NaN|Infinity/);
  }
});

test("explicit observation colors belong to discrete marks, not outgoing intervals", () => {
  const source = [{y: 1, color: "red"}, {y: 2, color: "blue"}, {y: 3, color: "green"}];
  assert.deepEqual(sparklinePoints(source, {}).map(([x]) => x), [0, 1, 2]);
  for (const type of ["bar", "points", "change", "line", "area"]) {
    const continuous = ["line", "area"].includes(type);
    const svg = renderSparkline(column(type, {color_options: {}, sparkline_options: {type, markers: true}}), source);
    const marks = [...svg.querySelectorAll(continuous || type === "points" ? "circle" : "rect")];
    assert.equal(marks[0].getAttribute("fill"), "red");
    assert.equal(marks[1].getAttribute("fill"), "blue");
    if (continuous) {
      assert.equal(svg.querySelectorAll("polyline").length, 1);
      assert.match(svg.querySelector("polyline").getAttribute("stroke"), /--et-accent/);
    }
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
  assert.equal(svg.querySelectorAll("polygon").length, 1);
  assert.match(svg.querySelector("polygon").getAttribute("fill"), /^url\(#/);
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

test("vertical paints clamp independently of geometry and retain narrow threshold anchors", () => {
  const col = column("area", {color_options: {color_stops: [
    {value: -1, color: "#00800000"}, {value: 0.4, color: "green"},
    {value: 0.40001, color: "red"}, {value: 1, color: "red"},
  ]}});
  const svg = renderSparkline(col, [-3, 3]);
  const gradient = svg.querySelector("linearGradient");
  assert.equal(gradient.firstElementChild.getAttribute("stop-opacity"), "0");
  assert.equal(gradient.lastElementChild.getAttribute("stop-color"), "#ff0000");
  assert.equal(gradient.lastElementChild.getAttribute("stop-opacity"), "1");
  const anchors = [...gradient.children].filter(stop => {
    const value = Number(stop.getAttribute("offset")) * 6 - 3;
    return Math.abs(value - 0.4) < 0.00002;
  });
  assert.deepEqual(anchors.map(stop => stop.getAttribute("stop-color")), ["#008000", "#ff0000"]);
  assert.equal(gradient.getAttribute("y1"), "28.5");
  assert.equal(gradient.getAttribute("y2"), "1.5");
  // Observed +/-3 remain at the chart extrema; color endpoints do not clip them.
  assert.equal(svg.querySelector("polyline").getAttribute("points"), "1.5,28.5 98.5,1.5");
});

test("area opacity ramps from the reference toward both edges while the outline stays solid", () => {
  const svg = renderSparkline(column("area", {color_options: {}, sparkline_options: {
    type: "area", color: "green", reference: 1, fill_opacity: [0, 0.6], width: 100, height: 30,
  }}), [-3, 0, 5]);
  assert.equal(svg.querySelector("polyline").getAttribute("stroke"), "green");
  const stops = [...svg.querySelectorAll("stop")];
  assert.equal(stops[0].getAttribute("stop-opacity"), "0.6");
  assert.equal(stops.at(-1).getAttribute("stop-opacity"), "0.6");
  assert.equal(stops.find(stop => stop.getAttribute("offset") === "0.5").getAttribute("stop-opacity"), "0");
  // A fixed opacity multiplies alpha in a color lookup, instead of replacing it.
  const alpha = renderSparkline(column("area", {color_options: {color_scale: ["#00ff0080", "#0000ff80"], min: 0, max: 5},
    sparkline_options: {type: "area", fill_opacity: 0.5}}), [0, 5]);
  const fillId = alpha.querySelector("polygon").getAttribute("fill").slice(5, -1);
  assert.equal(Number(alpha.querySelector(`[id="${fillId}"] stop`).getAttribute("stop-opacity")), 0.25);
});

test("gradient ids remain unique across widgets and constant, horizontal, and isolated runs stay finite", () => {
  const ids = new Set();
  for (const values of [[3, 3], [-3, null, 3], [0], [3, null, 3]]) {
    const svg = renderSparkline(column("area"), values);
    assert.doesNotMatch(svg.outerHTML, /NaN|Infinity/);
    for (const gradient of svg.querySelectorAll("linearGradient")) {
      assert.ok(!ids.has(gradient.id));
      ids.add(gradient.id);
    }
    assert.equal(svg.querySelectorAll("polyline").length, values.includes(null) ? 2 : 1);
  }
});
