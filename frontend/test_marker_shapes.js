import {test} from "node:test";
import assert from "node:assert/strict";
import {JSDOM} from "jsdom";
import {MARKER_SHAPES, markerGraphic, markerPath, markerAngle, symbolGeometry} from "./src/marker-shapes.js";
import {renderMarks, renderSymbols, renderSparkline} from "./src/visualizations.js";
import {renderLegends} from "./src/legends.js";
import {pointClusters, combinePoints} from "./src/point-clusters.js";

global.document = new JSDOM("<!doctype html><body></body>").window.document;
global.Node = document.defaultView.Node;

test("one geometry set supplies every shape, rotation and outline treatment", () => {
  assert.equal(new Set(MARKER_SHAPES.map(markerPath)).size, MARKER_SHAPES.length);
  assert.equal(markerPath("unknown"), markerPath("circle"));
  assert.equal(markerPath("__proto__"), markerPath("circle"));
  assert.equal(markerAngle("circle", 90), 0);
  assert.equal(markerAngle("cross", -45), 315);
  for (const shape of MARKER_SHAPES) for (const outline of [undefined, true, false, "navy"]) {
    const graphic = markerGraphic({shape, angle: 270, color: "red", outline});
    const path = graphic.querySelector("path");
    assert.equal(path.getAttribute("d"), markerPath(shape));
    assert.equal(path.getAttribute("fill"), "red");
    assert.equal(path.getAttribute("stroke"), outline === false ? "none" : outline === "navy" ? "navy"
      : "var(--et-marker-outline, color-mix(in srgb, Canvas 60%, transparent))");
  }
  assert.equal(markerGraphic({hollow: true, color: "gold"}).firstChild.getAttribute("stroke"), "gold");
});

test("scalar, array and named points retain geometry in their legends", () => {
  for (const kind of ["point", "points"]) for (const shape of MARKER_SHAPES) {
    const enc = {kind, source: "a", shape, angle: 45, outline: "black", color: "red"};
    const column = {name: "a", encodings: [enc], legend: true};
    const node = renderMarks(column, {a: kind === "points" ? [2, 3, null] : 2}, {min: 0, max: 4});
    const mark = node.querySelector(".et-mark-point");
    const key = renderLegends([column], [column], {}).querySelector(".et-legend-swatch");
    assert.equal(mark.dataset.shape, shape);
    assert.equal(key.dataset.shape, shape);
    assert.equal(mark.dataset.angle, key.dataset.angle);
    if (shape === "circle") assert.match(mark.style.boxShadow, /black/);
    else {
      assert.equal(mark.querySelector("path").getAttribute("d"), key.querySelector("path").getAttribute("d"));
      assert.equal(mark.querySelector("path").getAttribute("stroke"), "black");
      assert.equal(mark.style.backgroundColor, "transparent");
    }
  }
  const named = renderMarks({encodings: [{kind: "points", sources: ["a", "b"], shape: "star", outline: false}]},
    {a: 1, b: 2}, {min: 0, max: 3});
  assert.equal(named.querySelectorAll('[data-shape="star"]').length, 2);
});

test("familiar glyphs and explicit shapes share geometry, while custom text stays text", () => {
  for (const [symbol, shape] of [["■", "square"], ["●", "circle"], ["★", "star"], ["▲", "triangle"], ["◆", "diamond"]]) {
    const a = renderSymbols({symbol_options: {symbol}}, 2);
    const b = renderSymbols({symbol_options: {shape}}, 2);
    assert.deepEqual([...a.querySelectorAll("path")].map(p => p.getAttribute("d")),
      [...b.querySelectorAll("path")].map(p => p.getAttribute("d")));
  }
  const stars = renderSymbols({symbol_options: {symbol: "★", empty: "☆", max: 5, color: "gold"}}, 3);
  assert.equal(stars.querySelectorAll('[data-hollow="true"] path[fill="none"]').length, 2);
  assert.equal(stars.getAttribute("aria-label"), "3 of 5 symbols");
  const custom = renderSymbols({symbol_options: {symbol: "🐟", empty: "·", max: 3}}, 1);
  assert.equal(custom.textContent, "🐟··");
  assert.equal(custom.querySelectorAll("svg").length, 0);
  for (const symbol of ["constructor", "__proto__"]) {
    assert.equal(renderSymbols({symbol_options: {symbol}}, 1).textContent, symbol);
  }
  assert.equal(symbolGeometry({symbol: "×", angle: 90}, true).angle, 135);
  assert.equal(symbolGeometry({shape: "square", empty: "☆"}, false).hollow, true);
});

test("sparkline visible symbols and invisible observation targets both remain inspectable", () => {
  const column = {name: "a", sparkline_options: {type: "points", shape: "triangle", angle: 270, outline: "black"}};
  const node = renderSparkline(column, [1, null, 3]);
  assert.equal(node.querySelectorAll(".et-marker-svg").length, 2);
  assert.equal(node.querySelectorAll('[data-sparkline-observation="true"]').length, 2);
  for (const path of node.querySelectorAll(".et-marker-svg path")) assert.equal(path.getAttribute("transform"), "rotate(270)");
  const ends = renderSparkline({...column, sparkline_options: {...column.sparkline_options, type: "line", markers: "ends"}}, [1, 2, 3]);
  assert.equal(ends.querySelectorAll('[data-sparkline-observation="true"]').length, 3);
  assert.equal(ends.querySelectorAll(".et-marker-svg").length, 2);
});

test("overlap clusters require identical shape and angle and retain segmented noncircle geometry", () => {
  const dot = (shape, angle, color) => ({shape, angle, color, opaque: true, x: 10, y: 10, width: 12, height: 12});
  assert.equal(pointClusters([dot("square", 0, "red"), dot("circle", 0, "blue")]).length, 0);
  assert.equal(pointClusters([dot("triangle", 0, "red"), dot("triangle", 90, "blue")]).length, 0);
  const root = renderMarks({encodings: [{kind: "point", source: "a", shape: "star", angle: 45, color: "red", outline: "black"},
    {kind: "point", source: "b", shape: "star", angle: 45, color: "blue", outline: "black"}]}, {a: 2, b: 2});
  for (const mark of root.querySelectorAll(".et-mark-point")) mark.getBoundingClientRect = () => ({left: 10, top: 10, width: 12, height: 12});
  const holder = document.createElement("div"); holder.append(root); document.body.append(holder);
  combinePoints(holder);
  const composite = holder.querySelector(".et-point-composite");
  assert.ok(composite);
  assert.equal(composite.querySelector("clipPath path").getAttribute("d"), markerPath("star"));
  assert.equal(composite.querySelector("clipPath path").getAttribute("transform"), "rotate(45)");
  assert.ok(!composite.style.transform.includes("rotate"));
  assert.equal(composite.querySelectorAll("path[stroke=black]").length, 2);
  assert.equal(composite.querySelectorAll('path[fill="red"], path[fill="#ff0000"], path[fill="blue"], path[fill="#0000ff"]').length, 2);
  holder.remove();
});


test("sparkline circles can opt into an outline without changing their default geometry", () => {
  for (const outline of [true, "black", false]) {
    const node = renderSparkline({sparkline_options: {type: "points", outline}}, [1, 2]);
    const circle = node.querySelector("circle");
    assert.equal(circle.hasAttribute("stroke"), outline !== false);
  }
});


test("bar markers are vertical by default and rotate to horizontal", () => {
  const vertical = markerGraphic({shape: "bar"}).querySelector("path");
  assert.equal(vertical.getAttribute("d"), "M-10,-50 H10 V50 H-10 Z");
  assert.equal(vertical.getAttribute("transform"), "rotate(0)");
  assert.equal(markerGraphic({shape: "bar", angle: 90}).firstChild.getAttribute("transform"), "rotate(90)");
});


test("a composite keeps the paint order of its last member before later mixed shapes", () => {
  const node = renderMarks({encodings: [
    {kind: "point", source: "a", color: "red"}, {kind: "point", source: "b", color: "blue"},
    {kind: "point", source: "c", color: "green", shape: "square"},
  ]}, {a: 1, b: 1, c: 1});
  for (const mark of node.querySelectorAll(".et-mark-point")) mark.getBoundingClientRect = () => ({left: 10, top: 10, width: 7, height: 7});
  const holder = document.createElement("div"); holder.append(node); document.body.append(holder);
  combinePoints(holder);
  const composite = node.querySelector(".et-point-composite");
  assert.ok(composite);
  assert.equal(composite.nextElementSibling.dataset.shape, "square");
  holder.remove();
});


test("equilateral triangles rotate about their geometric centre", () => {
  const coordinates = markerPath("triangle").match(/-?\d+(?:\.\d+)?/g).map(Number);
  const [x0, y0, x1, y1, x2] = coordinates;
  const points = [[x0, y0], [x1, y1], [x2, y1]];
  const lengths = points.map((p, i) => Math.hypot(p[0] - points[(i + 1) % 3][0], p[1] - points[(i + 1) % 3][1]));
  assert.ok(Math.max(...lengths) - Math.min(...lengths) < 1e-9);
  assert.ok(Math.abs(points.reduce((sum, p) => sum + p[0], 0)) < 1e-9);
  assert.equal(points.reduce((sum, p) => sum + p[1], 0), 0);
});
