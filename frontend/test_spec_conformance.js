import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import { renderMarks, marksDomain, renderSparkline } from "./src/visualizations.js";
import { calculateVizRanges } from "./src/color.js";
import { sortRows, searchRows, paginateRows, sectionContinuation } from "./src/rows.js";
import { fitMarkLabels } from "./src/mark-labels.js";

global.document = new JSDOM("<!doctype html><html><body></body></html>").window.document;
global.Node = document.defaultView.Node;

test("fixed scale bounds win over automatic inclusion of zero", () => {
  assert.deepEqual(marksDomain({encodings: [{kind: "bar"}], scale: {domain: [10, 20]}}, {min: 12, max: 18}),
    {lo: 10, hi: 20, span: 10, transform: undefined});
});

test("missing scalar and array values suppress their marks, retaining siblings", () => {
  const encodings = [{kind: "bar", source: "v"}, {kind: "point", source: "v"},
    {kind: "range", source: "v", high: "target"}, {kind: "points", source: "samples"},
    {kind: "point", source: "target"}];
  const node = renderMarks({encodings}, {v: null, target: 7, samples: [null, 5]}, {min: 0, max: 10});
  assert.equal(node.querySelectorAll(".et-mark-bar, .et-mark-range").length, 0);
  assert.equal(node.querySelectorAll(".et-mark-point").length, 2);
});

test("a filled range stays vertically inside its track", () => {
  const node = renderMarks({encodings: [{kind: "range", source: "lo", high: "hi", fill: true}]},
    {lo: 2, hi: 8}, {min: 0, max: 10});
  assert.equal(node.firstChild.style.transform, "none");
});

test("diverging stacks use one magnitude scale across rows", () => {
  const encodings = ["a", "neutral", "b"].map(source => ({kind: "stacked_bar", source, diverge_at: "neutral"}));
  const col = {name: "a", encodings};
  const rows = [{a: 10, neutral: 0, b: 10}, {a: 10, neutral: 0, b: 30}];
  const range = calculateVizRanges([col], rows).get("a");
  const widths = rows.map(row => [...renderMarks(col, row, range).querySelectorAll(".et-mark-stack-seg")]
    .map(el => el.style.width));
  assert.equal(widths[0][1], widths[1][1]);
});

test("a target point does not count toward a cumulative stack total", () => {
  const col = {name: "a", encodings: [{kind: "stacked_bar", source: "a"},
    {kind: "stacked_bar", source: "b"}, {kind: "point", source: "target"}]};
  assert.deepEqual(calculateVizRanges([col], [{a: 20, b: 30, target: 40}]).get("a"), {min: 0, max: 50});
});

test("marks retain declaration order across mark kinds", () => {
  const node = renderMarks({encodings: [{kind: "point", source: "p"},
    {kind: "boxplot", parts: {minimum: "lo", q1: "lo", median: "p", q3: "hi", maximum: "hi"}}]},
    {p: 5, lo: 2, hi: 8}, {min: 0, max: 10});
  assert.equal(node.firstChild.className, "et-mark et-mark-point");
});

test("structured sparkline preserves irregular x positions and missing-value gaps", () => {
  const svg = renderSparkline({sparkline_options: {x: "x", y: "y", markers: true, width: 103}},
    [{x: 0, y: 2}, {x: 1, y: 4}, {x: 2, y: null}, {x: 10, y: 6}]);
  const dots = [...svg.querySelectorAll("circle")];
  assert.equal(dots.length, 3);
  assert.equal(Number(dots[1].getAttribute("cx")), 11.5);
  assert.equal(svg.querySelectorAll("polyline").length, 2);
});

test("null array observations do not expand the shared domain to zero", () => {
  const col = {name: "x", encodings: [{kind: "points", source: "x"}]};
  assert.deepEqual(calculateVizRanges([col], [{x: [null, 5, 8]}]).get("x"), {min: 5, max: 8});
});

const grouped = [
  {render_type: "row_section", __label: "North", __group_key: "n", __row_builder: true},
  {name: "Alpha", value: 1, __parent_key: "n", __ancestors: ["n"], __row_builder: true},
  {name: "Beta", value: 3, __parent_key: "n", __ancestors: ["n"], __row_builder: true},
  {render_type: "row_subtotal", __group_key: "n", __row_builder: true, value: 4},
  {render_type: "row_section", __label: "South", __group_key: "s", __row_builder: true},
  {name: "Gamma", value: 8, __parent_key: "s", __ancestors: ["s"], __row_builder: true},
  {render_type: "row_total", __row_builder: true, value: 12},
];

test("synthetic sections survive search with matching members", () => {
  const found = searchRows(grouped, [{name: "name"}], "Alpha", new Set());
  assert.deepEqual(found.map(row => row.__label || row.name || row.render_type), ["North", "Alpha", "row_subtotal", "row_total"]);
});

test("synthetic group identities keep sorting inside each section", () => {
  const sorted = sortRows(grouped, [{name: "value", type: "number"}], {column: "value", direction: "desc"});
  assert.deepEqual(sorted.filter(row => row.name).map(row => row.name), ["Beta", "Alpha", "Gamma"]);
});

test("builder summaries paginate and repeat only the current section", () => {
  const first = paginateRows(grouped, 2, 0, {});
  const second = paginateRows(grouped, 2, 1, {});
  assert.equal(first.rows.length, 2);
  assert.equal(second.pageCount, 4);
  assert.equal(sectionContinuation(grouped, second.start, second.rows), "North (cont.)");
  const last = paginateRows(grouped, 2, 3, {});
  assert.equal(sectionContinuation(grouped, last.start, last.rows), null);
});

test("array observations and scalar overlays both contribute to the domain", () => {
  const col = {name: "samples", encodings: [{kind: "points", source: "samples"}, {kind: "point", source: "target"}]};
  assert.deepEqual(calculateVizRanges([col], [{samples: [5, 10], target: 20}]).get("samples"), {min: 5, max: 20});
});

test("off-domain reference rules are omitted rather than moved to the boundary", () => {
  const node = renderMarks({encodings: [{kind: "point", source: "x"}],
    references: [{value: 25}], scale: {domain: [0, 10]}}, {x: 5}, null);
  assert.equal(node.querySelectorAll(".et-mark-reference").length, 0);
});

test("overflow arrows retain true endpoints in accessible text", () => {
  const node = renderMarks({encodings: [{kind: "range", source: "lo", high: "hi", cap: "line", overflow: "arrow"}],
    scale: {domain: [0, 10]}}, {lo: -5, hi: 15}, null);
  assert.equal(node.querySelectorAll(".et-mark-arrow").length, 2);
  assert.equal(node.querySelectorAll(".et-mark-cap:not(.et-mark-arrow)").length, 0);
  assert.match(node.getAttribute("aria-label"), /lo: -5, hi: 15/);
});

test("tiny segment labels hide completely and reappear when space becomes available", () => {
  const table = document.createElement("table");
  const cell = table.insertRow().insertCell();
  const node = renderMarks({encodings: [{kind: "stacked_bar", source: "a", label: {value: true}}]}, {a: 100}, {min: 0, max: 100});
  cell.append(node);
  const label = node.querySelector(".et-mark-stack-label");
  const segment = label.parentElement;
  cell.getBoundingClientRect = () => ({left: 0, right: 100});
  segment.getBoundingClientRect = () => ({left: 0, right: 10, width: 10});
  label.firstChild.getBoundingClientRect = () => ({width: 30});
  fitMarkLabels(table);
  assert.equal(label.style.visibility, "hidden");
  segment.getBoundingClientRect = () => ({left: 0, right: 100, width: 100});
  fitMarkLabels(table);
  assert.equal(label.style.visibility, "");
});

test("a missing categorical strip observation leaves an empty slot", () => {
  const node = renderMarks({encodings: [{kind: "strip", source: "states"}]}, {states: ["W", null, "L"]}, null);
  assert.equal(node.querySelectorAll(".et-strip-seg").length, 3);
  assert.equal(node.querySelectorAll(".et-strip-seg")[1].style.backgroundColor, "transparent");
});

test("a filled range supports overflow arrows too", () => {
  const node = renderMarks({encodings: [{kind: "range", source: "lo", high: "hi", fill: true, overflow: "arrow"}],
    scale: {domain: [0, 10]}}, {lo: -5, hi: 15}, null);
  assert.equal(node.querySelectorAll(".et-mark-range-fill .et-mark-arrow").length, 2);
});

test("conventional x/y sparkline struct fields work without explicit bindings", () => {
  const svg = renderSparkline({sparkline_options: {width: 103}}, [{x: 0, y: 2}, {x: 1, y: 5}, {x: 10, y: 8}]);
  const dots = [...svg.querySelectorAll("circle")];
  assert.equal(Number(dots[1].getAttribute("cx")), 11.5);
});

test("a two-sided magnitude domain also positions axes, references and points around zero", () => {
  const col = {encodings: [{kind: "bar", source: "a", side: "left"}, {kind: "point", source: "p"}],
    scale: {domain: [0, 100]}, references: [{value: 0}]};
  assert.equal(marksDomain(col, null).lo, -100);
  const node = renderMarks(col, {a: 20, p: 20}, null);
  assert.equal(node.querySelector(".et-mark-bar").style.left, "40%");
  assert.equal(node.querySelector(".et-mark-point").style.left, "60%");
  assert.equal(node.querySelector(".et-mark-reference").style.left, "50%");
});

test("labels on fills use white on dark colours, dark text on light colours, and explicit overrides", () => {
  for (const [fill, expected] of [["#111111", "rgb(255, 255, 255)"], ["#eeeeee", "rgb(0, 0, 0)"]]) {
    for (const kind of ["bar", "stacked_bar"]) {
      const node = renderMarks({encodings: [{kind, source: "a", color: fill,
        label: {value: true, position: "inside_end"}}]}, {a: 10}, {min: 0, max: 20});
      assert.equal(node.querySelector("[data-mark-label]").style.color, expected);
    }
  }
  const node = renderMarks({encodings: [{kind: "stacked_bar", source: "a", color: "black",
    label: {value: true, color: "yellow"}}]}, {a: 10}, {min: 0, max: 20});
  assert.equal(node.querySelector("[data-mark-label]").style.color, "yellow");
});

test("presentation slots reusing a source field retain independent domains", () => {
  const stack = {name: "a", encodings: [{kind: "stacked_bar", source: "a"}, {kind: "stacked_bar", source: "b"}]};
  const bar = {name: "a", encodings: [{kind: "bar", source: "a"}]};
  const ranges = calculateVizRanges([stack, bar], [{a: 50, b: 50}]);
  assert.deepEqual(ranges.get(stack), {min: 0, max: 100});
  assert.deepEqual(ranges.get(bar), {min: 50, max: 50});
});
