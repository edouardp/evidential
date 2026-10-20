import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import { readDensity, projectBand, renderDensityBand } from "./src/density-band.js";
import { renderMarks, scalePosition } from "./src/visualizations.js";
import { calculateVizRanges } from "./src/color.js";

global.document = new JSDOM("<!doctype html><body></body>").window.document;
global.Node = document.defaultView.Node;
const spec = {x: "position", y: "density", height: 0.5, density_max: null};
const curve = pairs => pairs.map(([position, density]) => ({position, density}));
const project = (data, config = spec, pos = x => x * 10) => projectBand(readDensity(data, config), config, pos);

test("uncertainty is a flat band whose opacity follows irregular quantitative positions", () => {
  const data = curve([[0, 0], [2, 1], [10, 0]]);
  assert.deepEqual(project(data), [{left: 0, width: 100, stops: [
    {offset: 0, alpha: 0}, {offset: 20, alpha: 1}, {offset: 100, alpha: 0},
  ]}]);
  const band = renderDensityBand({source: "curve", distribution: spec}, {curve: data}, x => x * 10, "#123456");
  assert.equal(band.tagName, "DIV");
  assert.equal(band.style.height, "50%");
  assert.equal(band.querySelectorAll("svg, path, polygon, polyline").length, 0);
  assert.match(band.firstChild.style.maskImage, /1\) 20%/);
});

test("a shared intensity ceiling compares density heights independently of physical height", () => {
  const config = {...spec, density_max: 2, height: 0.3};
  assert.equal(project(curve([[0, 0], [5, 1], [10, 0]]), config)[0].stops[1].alpha, 0.5);
  assert.equal(project(curve([[0, 0], [5, 2], [10, 0]]), config)[0].stops[1].alpha, 1);
  const saturated = project(curve([[0, 0], [5, 4], [10, 0]]), config)[0].stops;
  assert.deepEqual(saturated, [{offset: 0, alpha: 0}, {offset: 25, alpha: 1},
    {offset: 50, alpha: 1}, {offset: 75, alpha: 1}, {offset: 100, alpha: 0}]);
});

test("clipping interpolates boundary density without relocating samples or renormalizing the tail", () => {
  const data = curve([[-10, 0], [0, 2], [10, 0]]);
  assert.deepEqual(project(data, spec, x => (x + 5) * 10), [{left: 0, width: 100, stops: [
    {offset: 0, alpha: 0.5}, {offset: 50, alpha: 1}, {offset: 100, alpha: 0.5},
  ]}]);
  assert.deepEqual(project(data, spec, x => x - 50), []);
  assert.equal(project(data, spec, x => (x - 5) * 20)[0].stops[0].alpha, 0.5);
});

test("support ends at supplied coordinates and null observations leave transparent gaps", () => {
  const data = [...curve([[1, 1], [2, 2], [3, null], [4, 1], [5, 2]]), null,
    {position: 6, density: 2}, {position: null, density: 1}];
  assert.deepEqual(project(data).map(({left, width}) => [left, width]), [[10, 10], [40, 10]]);
  assert.equal(project(data)[0].stops[0].alpha, 0.5);
});

test("missing, zero, isolated and invalid inputs never become an invented curve", () => {
  for (const data of [null, [], [1, 2, 3], curve([[1, 1]]), curve([[1, 0], [2, 0]]),
    curve([[2, 1], [1, 2]]), curve([[1, -1], [2, 1]])]) {
    assert.equal(renderDensityBand({source: "d", distribution: spec}, {d: data}, x => x, "red"), null);
  }
});

test("valid density support and overlays share the domain, color bindings and accessible values", () => {
  const col = {name: "d", encodings: [{kind: "distribution", source: "d", distribution: spec, color_column: "ink"},
    {kind: "point", source: "median", color: "#111", outline: false}]};
  const data = {d: curve([[-100, null], [0, 0], [2, 1], [10, 0]]), median: 8, ink: "#123456"};
  const domain = calculateVizRanges([col], [data]).get(col);
  assert.deepEqual(domain, {min: 0, max: 10});
  const node = renderMarks(col, data, domain);
  assert.equal(node.querySelector(".et-mark-point").style.left, "80%");
  assert.equal(node.querySelector(".et-density-band-run").style.backgroundColor, "rgb(18, 52, 86)");
  assert.match(node.getAttribute("aria-label"), /median: 8/);
});

test("a logarithmic axis positions a density peak and its overlay identically", () => {
  const data = curve([[1, 0], [10, 1], [100, 0]]);
  assert.equal(project(data, spec, scalePosition(1, 100, "log"))[0].stops[1].offset, 50);
});

test("large supplied curves do not use argument spreads or one DOM element per sample", () => {
  const data = Array.from({length: 150000}, (_, position) => ({position, density: position % 10}));
  assert.equal(project(data, spec, x => x / 149999 * 100)[0].stops.length, data.length);
  const band = renderDensityBand({source: "d", distribution: spec}, {d: data.slice(0, 1000)}, x => x / 10, "red");
  assert.equal(band.children.length, 1);
});
