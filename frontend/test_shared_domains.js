import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import { applySharedDomains } from "./src/shared-domains.js";
import { RowPipeline } from "./src/derived.js";
import { marksDomain, renderMarks } from "./src/visualizations.js";
import { buildColorVizScale, getColorForValue } from "./src/color.js";
import { renderSparkline } from "./src/sparkline.js";
import { prepareChangeScales } from "./src/change-sparkline.js";

global.document = new JSDOM("<!doctype html><body></body>").window.document;
global.Node = document.defaultView.Node;
const bar = name => ({name, encodings: [{kind: "bar", source: name}], domain: {name: "counts", include_zero: true}});

test("marks and ordinary columns pool values, independently of headers and hidden membership", () => {
  const a = {...bar("a"), column_group: "One"};
  const b = {...bar("b"), column_group: "Two"};
  const anchor = {name: "limit", domain: {name: "counts"}, hide: true};
  const rows = [{a: 20, b: 20, limit: 200}, {a: 50, b: null, limit: 100}, {a: null, b: null, limit: ""},
    {a: 9999, limit: 9999, render_type: "row_total"}];
  const ranges = applySharedDomains([a, b, anchor], rows, new Map());
  assert.deepEqual(ranges.get(a), {min: 0, max: 200, shared: true});
  assert.equal(ranges.get(a), ranges.get(b));
  const width = column => renderMarks(column, rows[0], ranges.get(column)).querySelector(".et-mark-bar").style.width;
  assert.equal(width(a), "10%");
  assert.equal(width(a), width(b));
  assert.equal(marksDomain(a, ranges.get(a)).hi, 200);
});

test("centered members make the whole domain symmetric, including ordinary points and color", () => {
  const a = bar("a"); a.encodings[0].center = true;
  const b = {name: "b", encodings: [{kind: "point", source: "b"}], domain: {name: "counts"}};
  const ranges = applySharedDomains([a, b], [{a: -3, b: 8}], new Map());
  assert.deepEqual(ranges.get(a), {min: -8, max: 8, shared: true});
  assert.deepEqual(marksDomain(a, ranges.get(a)), marksDomain(b, ranges.get(b)));
});

test("stack totals, array marks and sparkline observations contribute their plotted values", () => {
  const stack = {name: "a", encodings: [{kind: "stacked_bar", source: "a"}, {kind: "stacked_bar", source: "b"}], domain: "x"};
  const points = {name: "p", encodings: [{kind: "points", source: "p"}], domain: "x"};
  const spark = {name: "s", viz: "sparkline", sparkline_options: {type: "line"}, domain: "x"};
  const ranges = applySharedDomains([stack, points, spark], [{a: 40, b: 60, p: [null, 20], s: [2, 200]}], new Map());
  assert.equal(ranges.get(stack).max, 200);
  assert.equal(ranges.get(points).max, 200);
  const svg = renderSparkline(spark, [0, 100], undefined, ranges.get(spark));
  assert.equal(svg.querySelector("polyline").getAttribute("points"), "1.5,16.5 62.5,9");
});

test("fixed bounds and opt-out zero policy stay shared for bars, points and empty members", () => {
  const a = {...bar("a"), domain: {name: "counts", bounds: [10, 100], include_zero: false}};
  const b = {...bar("b"), domain: {name: "counts", include_zero: false}};
  const ranges = applySharedDomains([a, b], [{a: 25, b: null}], new Map());
  assert.deepEqual(marksDomain(a, ranges.get(a)), {lo: 10, hi: 100, span: 90, transform: undefined});
  assert.equal(ranges.get(b).min, 10);
  const empty = applySharedDomains([a], [], new Map());
  assert.equal(empty.get(a).max, 100);
});

test("shared palettes and midpoint yield equal colors across different numeric columns", () => {
  const spec = {name: "temperature", palette: ["tab:red", "gray", "tab:blue"], midpoint: 0};
  const a = {name: "a", viz: "color", domain: spec};
  const b = {name: "b", viz: "chip", domain: spec};
  const range = {min: -2, max: 10, shared: true};
  const sa = buildColorVizScale(a, range);
  const sb = buildColorVizScale(b, range);
  assert.equal(getColorForValue(0, sa), "#808080");
  assert.equal(getColorForValue(0, sb), "#808080");
  assert.equal(getColorForValue(5, sa), getColorForValue(5, sb));
});

test("heatmap and change sparkline share a whole steady interval and the same color mapping", () => {
  const spec = {name: "change", palette: ["red", "gray", "blue"], neutral_range: [-0.5, 0.5]};
  const spark = {name: "a", viz: "sparkline", sparkline_options: {type: "change", steady: [-0.5, 0.5]}, domain: spec};
  const heat = {name: "b", viz: "color", domain: spec};
  const rows = [{a: [-4, 0.2, 1, 8], b: 0.2}];
  const ranges = applySharedDomains([spark, heat], rows, new Map());
  const color = prepareChangeScales([spark], rows, ranges).get(spark);
  const heatScale = buildColorVizScale(heat, ranges.get(heat));
  for (const value of [-4, -0.5, 0, 0.2, 0.5, 4, 8]) assert.equal(color(value), getColorForValue(value, heatScale));
  assert.equal(color(0.2), "#808080");
});

test("filtering recomputes domains, while paging and sorting do not change their meaning", () => {
  const a = bar("a"), b = bar("b");
  const pipeline = new RowPipeline();
  const args = {rows: [{name: "North", a: 20, b: 200}, {name: "South", a: 10, b: 100}],
    columns: [{name: "name"}, a, b], options: {page_size: 1}, search: "", hidden: new Set(["b"]), sort: null};
  const all = pipeline.get(args);
  assert.equal(all.ranges.get(a).max, 200);
  assert.equal(pipeline.get(args), all);
  assert.equal(pipeline.get({...args, search: "South"}).ranges.get(a).max, 100);
  assert.equal(pipeline.get({...args, sort: {column: "a", direction: "desc"}}).ranges.get(a).max, 200);
});
