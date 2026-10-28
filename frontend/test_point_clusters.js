import {test} from "node:test";
import assert from "node:assert/strict";
import {JSDOM} from "jsdom";
import {pointClusters, combinePoints, pointVisual} from "./src/point-clusters.js";

const dot = (x, color = "red", y = 10, extra = {}) => ({x, y, color, opaque: true, width: 12, height: 12, ...extra});

test("cluster bounds never chain beyond one pixel, even across a long ladder", () => {
  const points = Array.from({length: 21}, (_, i) => dot(i, i % 2 ? "blue" : "red"));
  const clusters = pointClusters(points);
  assert.equal(clusters.length, 10);
  for (const cluster of clusters) assert.ok(Math.max(...cluster.map(point => point.x)) - Math.min(...cluster.map(point => point.x)) <= 1);
  assert.deepEqual(pointClusters([dot(0), dot(0.8, "blue"), dot(1.6, "green")]).map(group => group.length), [2]);
  assert.equal(pointClusters([dot(0), dot(0.9, "blue", 10.9)]).length, 0);
});

test("only compatible opaque circles of differing colors combine, without mutating inputs", () => {
  const points = Object.freeze([Object.freeze(dot(10, "blue")), Object.freeze(dot(10, "red")), Object.freeze(dot(10, "green"))]);
  assert.equal(pointClusters(points)[0].length, 3);
  for (const b of [dot(10, "blue"), dot(10, "red", 10, {opaque: false}), dot(10, "red", 10, {width: 15}), dot(12, "red")]) {
    assert.equal(pointClusters([dot(10, "blue"), b]).length, 0);
  }
});

test("segmented circles retain original nodes, outlines and declaration-order sectors and separate on resize", () => {
  const dom = new JSDOM("<!doctype html><body></body>");
  global.document = dom.window.document;
  global.Node = dom.window.Node;
  const root = document.createElement("div");
  root.innerHTML = '<div class="et-marks"></div>';
  document.body.append(root);
  const track = root.firstChild;
  let spacing = 0.5;
  for (const [i, color] of ["red", "blue", "green"].entries()) {
    const node = document.createElement("div");
    node.className = "et-mark-point";
    node.style.cssText = `left:${50 + i / 10}%;top:50%;width:12px;height:12px;background:${color};box-shadow:rgb(0, 0, 0) 0px 0px 0px 1px`;
    node.getBoundingClientRect = () => ({left: 100 + i * spacing, top: 5, width: 12, height: 12});
    track.append(node);
  }
  const originals = [...track.children];
  combinePoints(root);
  const composite = track.querySelector(".et-point-composite");
  assert.equal(composite.dataset.pointCount, "3");
  assert.deepEqual([...composite.querySelectorAll("path[fill]:not([fill=none])")].map(node => node.getAttribute("fill")), ["#ff0000", "#0000ff", "#008000"]);
  assert.equal(composite.querySelectorAll("path[stroke]").length, 3);
  assert.equal(track.querySelectorAll(".et-mark-point").length, 3);
  assert.ok(originals.every(node => pointVisual(node) === composite));
  spacing = 10;
  combinePoints(root);
  assert.equal(track.querySelector(".et-point-composite"), null);
  assert.ok(originals.every(node => pointVisual(node) === node && !node.classList.contains("et-point-combined-member")));
  root.remove();
});
