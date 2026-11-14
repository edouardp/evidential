import {test} from "node:test";
import assert from "node:assert/strict";
import {JSDOM} from "jsdom";
import {renderMarks} from "./src/visualizations.js";
import {rangePaint} from "./src/range-paint.js";
import {scalePosition} from "./src/mark-scales.js";
import {createColorScale, getColorForValue} from "./src/color.js";

global.document = new JSDOM("<!doctype html>").window.document;
global.Node = document.defaultView.Node;
const range = {kind: "range", source: "low", high: "high", cap: "round"};
const gradient = {color_scale: ["#00ffff", "#ffff00"], min: 0, max: 100};
function paint(low, high, options = {}, transform, reverse = false) {
  const lo = transform ? 1 : 0, hi = 100;
  const enc = {...range, gradient, ...options};
  const view = {row: {low, high}, col: {scale: {transform}}, lo, hi, reverse,
    pos: scalePosition(lo, hi, transform, reverse)};
  const positions = [view.pos(low), view.pos(high)].map(value => Math.max(0, Math.min(100, value)));
  return rangePaint(enc, view, Math.min(...positions), Math.max(...positions), "red");
}

test("round caps stay within endpoints and clipping preserves square cut edges", () => {
  assert.equal(paint(20, 80).style.borderRadius, "999px 999px 999px 999px");
  assert.equal(paint(-20, 80).style.borderRadius, "0 999px 999px 0");
  assert.equal(paint(20, 180).style.borderRadius, "999px 0 0 999px");
  assert.equal(paint(-20, 180).style.borderRadius, "0 0 0 0");
  assert.equal(paint(80, 20).style.borderRadius, paint(20, 80).style.borderRadius);
  assert.equal(paint(0, 100, {cap: "line"}).style.borderRadius, undefined);
  assert.equal(paint(0, 100, {gradient: undefined}).at(20), "red");
});

test("range gradients sample a common x domain, clamp colors and preserve alpha", () => {
  const first = paint(20, 60), second = paint(40, 80);
  assert.equal(first.at(50), second.at(50));
  assert.equal(first.style.backgroundColor, "transparent");
  assert.match(first.style.backgroundImage, /^linear-gradient\(to right,/);
  assert.equal(paint(20, 60).style.backgroundImage, paint(60, 20).style.backgroundImage);
  const clamped = paint(0, 100, {gradient: {...gradient, min: 20, max: 80}});
  assert.equal(clamped.at(0), "#00ffff");
  assert.equal(clamped.at(100), "#ffff00");
  const transparent = paint(0, 100, {gradient: {color_stops: [
    {value: 0, color: "#00ff0000"}, {value: 100, color: "#00ff00ff"}]}});
  assert.match(transparent.style.backgroundImage, /#00ff0000 0%/);
});

test("log and reversed coordinates keep colors attached to numeric values", () => {
  const log = paint(1, 100, {}, "log");
  const scale = createColorScale([], {colorPalette: gradient.color_scale, min: 0, max: 100});
  assert.equal(log.at(50), getColorForValue(10, scale));
  const reverse = paint(20, 80, {}, undefined, true);
  assert.equal(reverse.at(20), paint(20, 80).at(80));
  const stops = paint(0, 100, {gradient: {color_stops: [
    {value: 0, color: "red"}, {value: 42.01, color: "white"}, {value: 100, color: "blue"}]}});
  assert.match(stops.style.backgroundImage, /#ffffff 42\.01%/);
});

test("rounded gradients compose with points, filled bands, endpoint caps and overflow arrows", () => {
  for (const options of [{}, {fill: true}, {cap: "line"}, {cap: "dot"}, {overflow: "arrow"}]) {
    const node = renderMarks({encodings: [{...range, gradient, direction_marker: true, ...options},
      {kind: "point", source: "current", color: "white"}], scale: {domain: [0, 100]}},
    {low: -10, high: 80, current: 50});
    const mark = node.querySelector(".et-mark-range, .et-mark-range-fill");
    assert.ok(mark.style.backgroundImage);
    assert.equal(node.querySelectorAll(".et-mark-point").length, 1);
    assert.ok(node.querySelector(".et-range-direction"));
    if (options.cap === "line" || options.cap === "dot") {
      assert.equal(mark.querySelector(".et-mark-cap-start").style.backgroundColor, "rgb(0, 255, 255)");
    }
  }
  for (const [low, high] of [[null, 8], [8, null]]) {
    const node = renderMarks({encodings: [{...range, gradient}]}, {low, high});
    assert.equal(node.querySelector(".et-mark-range"), null);
  }
  assert.ok(paint(20, 20).style.backgroundImage);
});
