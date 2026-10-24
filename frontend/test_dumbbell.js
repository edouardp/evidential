import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import { renderMarks } from "./src/visualizations.js";

const dom = new JSDOM("<!doctype html>");
global.document = dom.window.document;
global.Node = dom.window.Node;

const range = {kind: "range", source: "before", high: "after", color: "black", color_negative: "red", direction_marker: true};
const render = (before, after, options = {}) => renderMarks(
  {encodings: [{...range, ...options}], scale: {domain: [-20, 20]}}, {before, after});

test("range color follows the change between endpoints, including negative-valued increases", () => {
  for (const [before, after, color, direction] of [
    [8, 10, "black", "right"], [10, 8, "red", "left"],
    [-10, -8, "black", "right"], [-8, -10, "red", "left"],
    [5, 5, "black", null],
  ]) {
    const node = render(before, after, {cap: "line"});
    assert.equal(node.querySelector(".et-mark-range").style.backgroundColor, color);
    assert.equal(node.querySelector(".et-range-direction")?.dataset.direction || null, direction);
    for (const cap of node.querySelectorAll(".et-mark-cap")) assert.equal(cap.style.backgroundColor, color);
  }
});

test("negative range color can be row-bound and falls back to the ordinary color", () => {
  const column = {encodings: [{...range, color_negative: undefined, color_negative_column: "ink"}]};
  const node = renderMarks(column, {before: 10, after: 8, ink: "#cc0000"});
  assert.equal(node.querySelector(".et-mark-range").style.backgroundColor, "rgb(204, 0, 0)");
  assert.equal(render(10, 8, {color_negative: undefined}).querySelector(".et-mark-range").style.backgroundColor, "black");
});

test("direction is opt-in, missing endpoints omit the range, and points keep independent colors", () => {
  assert.equal(render(8, 10, {direction_marker: false}).querySelector(".et-range-direction"), null);
  for (const [before, after] of [[null, 8], [8, null]]) {
    assert.equal(render(before, after).querySelector(".et-range-direction"), null);
    assert.equal(render(before, after).querySelector(".et-mark-range"), null);
  }
  const node = renderMarks({encodings: [range,
    {kind: "point", source: "before", color: "blue"}, {kind: "point", source: "after", color: "orange"}]},
    {before: 10, after: 8});
  assert.deepEqual([...node.querySelectorAll(".et-mark-point")].map(point => point.style.backgroundColor), ["blue", "orange"]);
});

test("direction uses projected geometry while negative color uses the original change", () => {
  const node = renderMarks({scale: {domain: [1, 100], transform: "log"}, encodings: [range]}, {before: 50, after: 10});
  assert.equal(node.querySelector(".et-range-direction").dataset.direction, "left");
  const mirrored = renderMarks({scale: {domain: [0, 20]}, encodings: [range,
    {kind: "bar", source: "zero", direction: "left"}]}, {before: 10, after: 8, zero: 0});
  assert.equal(mirrored.querySelector(".et-range-direction").dataset.direction, "right");
  assert.equal(mirrored.querySelector(".et-mark-range").style.backgroundColor, "red");
});

test("clipping arrows and filled ranges retain signed colors and optional direction", () => {
  const clipped = render(30, -30, {overflow: "arrow", cap: "line"});
  assert.equal(clipped.querySelectorAll(".et-mark-arrow").length, 2);
  assert.equal(clipped.querySelector(".et-range-direction").dataset.direction, "left");
  assert.equal(render(40, 30).querySelector(".et-range-direction"), null);
  const filled = render(10, 8, {fill: true});
  assert.equal(filled.querySelector(".et-mark-range-fill").style.backgroundColor, "red");
  assert.equal(filled.querySelector(".et-range-direction").parentElement, filled);
  assert.equal(filled.querySelector(".et-range-direction").style.color, "red");
});
