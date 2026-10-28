import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import { seriesColors, COLORMAPS, calculateVizRanges } from "./src/color.js";
import { renderMarks } from "./src/visualizations.js";
import { renderLegends } from "./src/legends.js";

global.document = new JSDOM("<!doctype html><body></body>").window.document;
global.Node = document.defaultView.Node;

const series = {name: "young", fmt: "pct0", legend: true, scale: {domain: [0, 1]}, encodings: [
  {kind: "points", source: "young", sources: ["young", "middle", "old"], names: {young: "0–9", middle: "40–49", old: "80+"},
    connect: true, palette: "viridis", outline: false},
]};

test("series colors use a categorical default or sample a named or explicit range", () => {
  assert.deepEqual(seriesColors(3), ["#1f77b4", "#ff7f0e", "#2ca02c"]);
  assert.deepEqual(seriesColors(9, "viridis"), COLORMAPS.viridis);
  const custom = seriesColors(3, ["red", "blue"]);
  assert.equal(custom[0], "#ff0000");
  assert.equal(custom[2], "#0000ff");
  assert.equal(new Set(custom).size, 3);
  assert.deepEqual(seriesColors(3, ["red"]), ["red", "red", "red"]);
  assert.deepEqual(seriesColors(0), []);
  assert.notEqual(seriesColors(1, "viridis")[0], COLORMAPS.viridis[0]);
});

test("wide point marks and their legend share sampled fills and named identities", () => {
  const row = {young: 0.3, middle: 0.2, old: 0.1};
  const before = structuredClone(row);
  const node = renderMarks(series, row);
  const legend = renderLegends([series], [series], {});
  assert.deepEqual([...legend.querySelectorAll(".et-legend-label")].map(n => n.textContent), ["0–9", "40–49", "80+"]);
  assert.deepEqual([...legend.querySelectorAll(".et-legend-swatch")].map(n => n.style.backgroundColor),
    [...node.querySelectorAll(".et-mark-point")].map(n => n.style.backgroundColor));
  const connector = node.querySelector(".et-point-connector");
  assert.equal(connector.style.left, "10%");
  assert.equal(connector.style.width, "20%");
  assert.equal(legend.querySelector(".et-legend-swatch-range"), null);
  assert.deepEqual([...node.querySelectorAll(".et-mark-point")].map(n => n.title), ["0–9: 30%", "40–49: 20%", "80+: 10%"]);
  assert.deepEqual(row, before);
});

test("missing fields never turn into zero or recolor later series, and singleton/equal points have no span", () => {
  const colors = row => [...renderMarks(series, row).querySelectorAll(".et-mark-point")].map(n => n.style.backgroundColor);
  const all = colors({young: 0.3, middle: 0.2, old: 0.1});
  assert.deepEqual(colors({young: null, middle: 0.2, old: 0.1}), all.slice(1));
  for (const row of [{young: 0.3}, {young: null}, {young: 0.3, old: 0.3}]) {
    assert.equal(renderMarks(series, row).querySelector(".et-point-connector"), null);
  }
  const range = calculateVizRanges([series], [{young: null, middle: 0.2, old: 0.1}]).get("young");
  assert.deepEqual(range, {min: 0.1, max: 0.2});
  const noConnection = {...series, encodings: [{...series.encodings[0], connect: false}]};
  assert.equal(renderMarks(noConnection, {young: 0.2, middle: 0.3}).querySelector(".et-point-connector"), null);
});

test("explicit point colors override a palette and legends can rename or omit individual fields", () => {
  const column = {...series, legend: {middle: null, old: "Older"}, encodings: [{...series.encodings[0], color: "red"}]};
  const legend = renderLegends([column], [column], {});
  assert.deepEqual([...legend.querySelectorAll(".et-legend-label")].map(n => n.textContent), ["0–9", "Older"]);
  assert.deepEqual([...legend.querySelectorAll(".et-legend-swatch")].map(n => n.style.backgroundColor), ["red", "red"]);
});
