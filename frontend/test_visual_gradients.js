import {test} from "node:test";
import assert from "node:assert/strict";
import {JSDOM} from "jsdom";
import {renderMarks} from "./src/visualizations.js";
import {gradientColor, gradientPaint} from "./src/mark-gradient.js";
import {inspectionData} from "./src/tooltips.js";
import {scalePosition} from "./src/mark-scales.js";
import {projectBand} from "./src/density-band.js";

global.document = new JSDOM("<!doctype html>").window.document;
global.Node = document.defaultView.Node;
const gradient = {color_stops: [{value: -10, color: "#ff0000"}, {value: 0, color: "#ffffff00"}, {value: 10, color: "#0000ff"}]};
const column = encodings => ({encodings, scale: {domain: [-10, 10]}});
const view = (reverse = false, transform) => ({col: {scale: {transform}}, lo: transform ? 1 : -10, hi: transform ? 100 : 10,
  reverse, pos: scalePosition(transform ? 1 : -10, transform ? 100 : 10, transform, reverse)});

test("bar/range spans share paints; points sample the same lookup and preserve alpha", () => {
  const data = {low: -10, high: 10, x: 10, a: [-10, 0, 10]};
  const node = renderMarks(column([{kind: "range", source: "low", high: "high", gradient},
    {kind: "bar", source: "x", gradient}, {kind: "points", source: "a", gradient, outline: false}]), data);
  const marks = node.querySelectorAll(".et-mark-point");
  assert.deepEqual([...marks].map(mark => mark.style.backgroundColor), ["rgb(255, 0, 0)", "rgba(255, 255, 255, 0)", "rgb(0, 0, 255)"]);
  assert.deepEqual([...marks].map(mark => inspectionData(mark).color), ["#ff0000", "#ffffff00", "#0000ff"]);
  assert.ok(node.querySelector(".et-mark-bar").style.backgroundImage);
  assert.ok(node.querySelector(".et-mark-range").style.backgroundImage);
  const low = gradientPaint({gradient}, view(), 0, 50), high = gradientPaint({gradient}, view(), 50, 100);
  assert.equal(low.at(50), high.at(50));
});

test("bar labels sample their own anchor and reversed coordinates retain value colors", () => {
  for (const [position, color] of [["inside_start", "rgb(0, 0, 0)"], ["inside_end", "rgb(255, 255, 255)"]]) {
    const node = renderMarks(column([{kind: "bar", source: "x", gradient,
      label: {value: true, position}}]), {x: 10});
    assert.equal(node.querySelector(".et-mark-label").style.color, color);
  }
  const enc = {kind: "bar", source: "x", gradient, direction: "left"};
  const node = renderMarks(column([enc]), {x: 10});
  assert.equal(inspectionData(node.querySelector(".et-mark-bar")).color, "#0000ff");
  assert.equal(gradientPaint({gradient}, view(true), 0, 100).at(0), "#0000ff");
  const logView = view(false, "log");
  const paint = gradientPaint({gradient: {color_scale: ["red", "blue"], min: 1, max: 100}}, logView, 0, 100);
  assert.equal(paint.at(50), paint.colorAt(10));
});

test("point gradients clamp, handle constant domains and preserve solid marker shapes", () => {
  const config = {gradient: {color_scale: ["red", "blue"], min: -10, max: 10}};
  assert.equal(gradientColor(config, view(), -100), "#ff0000");
  assert.equal(gradientColor(config, view(), 100), "#0000ff");
  const constant = {...view(), lo: 3, hi: 3};
  assert.notEqual(gradientColor({gradient: {color_scale: ["red", "blue"]}}, constant, 3), "#ff0000");
  const node = renderMarks(column([{kind: "point", source: "x", gradient, shape: "star", outline: "black"}]), {x: 10});
  assert.equal(node.querySelector(".et-mark-point").style.color, "rgb(0, 0, 255)");
  assert.equal(node.querySelector("path").getAttribute("stroke"), "black");
  assert.equal(inspectionData(node.querySelector(".et-mark-point")).color, "#0000ff");
});

test("boxplot spans, median, caps and outliers share numeric colors in either direction", () => {
  const row = {low: -10, q1: -5, median: 0, q3: 5, high: 10, outliers: [-20, 20], zero: 0};
  const box = {kind: "boxplot", source: "median", parts: {minimum: "low", q1: "q1", median: "median", q3: "q3", maximum: "high"}, outliers: "outliers", gradient};
  for (const reverse of [false, true]) {
    const node = renderMarks(column([box, ...(reverse ? [{kind: "bar", source: "zero", direction: "left"}] : [])]), row);
    assert.ok(node.querySelector(".et-box-whisker").style.backgroundImage);
    assert.equal(node.querySelector(".et-box-iqr").style.width, "50%");
    assert.ok(node.querySelector(".et-box-iqr").style.borderImageSource);
    assert.deepEqual([...node.querySelectorAll(".et-box-outlier")].map(mark => inspectionData(mark).color), ["#ff0000", "#0000ff"]);
  }
});

test("density keeps its opacity mask, clipping and gaps while reversing without changing the source", () => {
  const runs = [[{x: -10, density: 0}, {x: 0, density: 1}, {x: 10, density: 0}]];
  const before = JSON.stringify(runs);
  const projected = projectBand(runs, {density_max: 1}, x => 50 - x * 5);
  assert.equal(projected[0].width, 100);
  assert.equal(projected[0].stops[1].alpha, 1);
  assert.equal(JSON.stringify(runs), before);
  const enc = {kind: "distribution", source: "curve", distribution: {x: "x", y: "density", height: 0.5}, gradient};
  const node = renderMarks(column([enc]), {curve: runs[0]});
  const band = node.querySelector(".et-density-band-run");
  assert.ok(band.style.backgroundImage);
  assert.ok(band.style.maskImage);
});
