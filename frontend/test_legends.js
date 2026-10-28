import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import { renderLegends } from "./src/legends.js";
import { markSeries } from "./src/mark-series.js";
import { renderMarks } from "./src/visualizations.js";

global.document = new JSDOM("<!doctype html><body></body>").window.document;
global.Node = document.defaultView.Node;

const stack = {name: "storage_cost", title: "Monthly cost", legend: true, encodings: [
  {kind: "stacked_bar", source: "storage_cost", color: "tab:blue"},
  {kind: "stacked_bar", source: "requests", color: "#f59e0b"},
]};

test("legends use source names rather than the compound column title and match real fills", () => {
  const node = renderLegends([stack], [stack], {});
  assert.equal(node.getAttribute("aria-label"), "Legend");
  assert.equal(node.querySelector(".et-legend-column"), null);
  assert.equal(node.querySelector('[role="group"]').getAttribute("aria-label"), "Monthly cost");
  assert.deepEqual([...node.querySelectorAll(".et-legend-label")].map(n => n.textContent), ["Storage Cost", "Requests"]);
  const marks = renderMarks(stack, {storage_cost: 12, requests: 3});
  assert.deepEqual([...node.querySelectorAll(".et-legend-swatch")].map(n => n.style.backgroundColor),
    [...marks.querySelectorAll(".et-mark-stack-seg")].map(n => n.style.backgroundColor));
});

test("names honor source overrides, formatting options and subcolumn heading joins", () => {
  const sources = [stack, {name: "requests", title: "API calls", hide: true}];
  const named = {...stack, legend_options: {column_names: true}};
  assert.deepEqual(markSeries(stack, sources).map(s => s.label), ["Storage Cost", "API calls"]);
  assert.equal(renderLegends([named], sources, {format_titles: false}).querySelector(".et-legend-column").textContent,
    "storage_cost");
  assert.equal(renderLegends([named], sources, {all_caps: true}).querySelector(".et-legend-column").textContent,
    "MONTHLY COST");
  assert.equal(renderLegends([{...named, subcolumn_group: "Combined"}], sources, {})
    .querySelector(".et-legend-column").textContent, "Combined");
  assert.equal(renderLegends([named], sources, {stub: "storage_cost", stub_head: "Costs"})
    .querySelector(".et-legend-column").textContent, "Costs");
});

test("column names default off for one nonempty group and on for several, with explicit overrides", () => {
  const second = {...stack, name: "b", title: "Traffic"};
  assert.equal(renderLegends([stack], [stack, second], {}).querySelectorAll(".et-legend-column").length, 0);
  assert.equal(renderLegends([stack, second], [stack, second], {}).querySelectorAll(".et-legend-column").length, 2);
  const forced = {...stack, legend_options: {column_names: true}};
  assert.equal(renderLegends([forced], [forced], {}).querySelectorAll(".et-legend-column").length, 1);
  const hidden = {...stack, legend_options: {column_names: false}};
  assert.deepEqual([...renderLegends([hidden, second], [hidden, second], {}).querySelectorAll(".et-legend-column")]
    .map(n => n.textContent), ["Traffic"]);
  const empty = {...second, legend: [null, null]};
  assert.equal(renderLegends([stack, empty], [stack, empty], {}).querySelectorAll(".et-legend-column").length, 0);
});

test("each column gets its own row without a redundant visible legend heading", () => {
  const second = {...stack, name: "other", title: "Traffic", legend: ["Web", "Mobile"]};
  const node = renderLegends([stack, second], [stack, second], {});
  assert.equal(node.querySelectorAll(".et-legend-title").length, 0);
  assert.deepEqual([...node.querySelectorAll('[role="group"]')].map(n => n.getAttribute("aria-label")),
    ["Monthly cost", "Traffic"]);
  assert.deepEqual([...node.querySelectorAll(".et-legend-label")].slice(2).map(n => n.textContent), ["Web", "Mobile"]);
  assert.equal(renderLegends([{...stack, legend: false}, {name: "plain"}], [], {}), null);
});

test("an opted-in column can outline the whole combined legend", () => {
  assert.equal(renderLegends([stack], [stack], {}).classList.contains("et-legends-outlined"), false);
  const outlined = {...stack, name: "b", legend_options: {outline: true}};
  const node = renderLegends([stack, outlined], [stack, outlined], {});
  assert.equal(node.classList.contains("et-legends-outlined"), true);
  assert.equal(node.querySelectorAll(".et-legend-group").length, 2);
  assert.equal(node.querySelectorAll(".et-legends-outlined").length, 0); // One box, on the container itself.
  assert.equal(renderLegends([stack, {...outlined, legend: false}], [], {})
    .classList.contains("et-legends-outlined"), false);
});

test("strip keys keep category order, source colors and explicit names without parsing HTML", () => {
  const strip = {name: "form", legend: {W: "Win", D: "Draw", L: "<b>Loss</b>"},
    encodings: [{kind: "strip", source: "form", colors: {W: "navy", D: "grey", L: "red"}}]};
  const node = renderLegends([strip], [strip], {});
  assert.deepEqual([...node.querySelectorAll(".et-legend-label")].map(n => n.textContent), ["Win", "Draw", "<b>Loss</b>"]);
  assert.equal(node.querySelector("b"), null);
  assert.deepEqual([...node.querySelectorAll(".et-legend-swatch")].map(n => n.style.backgroundColor),
    ["navy", "grey", "red"]);
});

test("overlay marks retain their shapes, negative colors and theme-aware default fills", () => {
  const col = {name: "actual", legend: true, encodings: [
    {kind: "bar", source: "actual", color: "navy", color_negative: "red"},
    {kind: "point", source: "target"},
  ]};
  const node = renderLegends([col], [col], {});
  assert.deepEqual([...node.querySelectorAll(".et-legend-label")].map(n => n.textContent),
    ["Actual", "Actual (negative)", "Target"]);
  assert.equal(node.querySelectorAll(".et-legend-swatch-bar").length, 2);
  assert.equal(node.querySelector(".et-legend-swatch-point").style.backgroundColor, "var(--et-accent, #2563eb)");
});

test("omitted connecting marks leave only the named points, with no empty legends", () => {
  const col = {name: "low", legend: {low: null, young: "0–9", old: "80+"}, encodings: [
    {kind: "range", source: "low", high: "high", color: "grey"},
    {kind: "point", source: "young", color: "blue"},
    {kind: "point", source: "old", color: "red"},
  ]};
  const node = renderLegends([col], [col], {});
  assert.deepEqual([...node.querySelectorAll(".et-legend-label")].map(n => n.textContent), ["0–9", "80+"]);
  assert.equal(node.querySelector(".et-legend-swatch-range"), null);
  assert.equal(renderLegends([{...col, legend: [null, null, null]}], [], {}), null);
});
