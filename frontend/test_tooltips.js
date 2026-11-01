import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import { fullNumber, tooltipValue, markTooltip, tooltipText } from "./src/tooltip-data.js";
import { inspectable, inspectCell, inspectionData, hitTargets, TooltipController } from "./src/tooltips.js";
import { renderMarks } from "./src/visualizations.js";
import { renderSparkline } from "./src/sparkline.js";

const dom = new JSDOM("<!doctype html><body></body>", {pretendToBeVisual: true});
global.document = dom.window.document;
global.Node = dom.window.Node;

test("full values expand scientific notation and compact formats without discarding precision", () => {
  for (const [value, expected] of [[1253224564.12, "1,253,224,564.12"], [1.23456e-7, "0.000000123456"],
    [1.234e21, "1,234,000,000,000,000,000,000"], [0, "0"], [-1234.5, "-1,234.5"]]) {
    assert.equal(fullNumber(value), expected);
    for (const code of ["compact", "compact4", "num0", "num1b", "sci"]) assert.equal(tooltipValue(value, code), expected);
  }
  assert.equal(tooltipValue(0.123456, "pct0"), "12.3456%");
  assert.equal(tooltipValue(0.331234, "pct"), "33.1234%");
  assert.equal(tooltipValue(-1253224564.12, "usd0b"), "-$1,253,224,564.12");
  assert.equal(tooltipValue(-1234.56, "eur0", {bracket_negatives: true}), "(€1,234.56)");
  assert.equal(tooltipValue(1234.56, "cad"), "C$1,234.56");
  assert.equal(tooltipValue(1234.56, '#,##0.0" kg"'), "1,234.56 kg");
  assert.equal(tooltipValue(1234.56, '"USD "#,##0.0;"USD "-#,##0.0'), "USD 1,234.56");
  assert.equal(tooltipValue(1024, "bytes"), "1,024 bytes");
  assert.equal(tooltipValue("001234", "id"), "001234");
  assert.equal(tooltipValue(null, "num0"), "–");
  assert.equal(tooltipValue("2024-01-02", "date"), "2024-01-02");
});

test("stack amounts, shares and totals ignore the drawn label's numeric format", () => {
  const enc = {kind: "stacked_bar", source: "storage", label: {share: true, format: "pct0"}};
  const col = {name: "storage", fmt: "usd0", scale: {normalize: "percent"}, encodings: [enc]};
  const data = markTooltip(col, enc, {storage: 1235}, {total: 2018});
  assert.equal(tooltipText(data), "Storage: 61%\nValue: $1,235\nTotal: $2,018");
  const value = markTooltip({...col, scale: {}}, {...enc, label: null}, {storage: 1235}, {total: 2018});
  assert.equal(tooltipText(value), "Storage: $1,235\nShare: 61.2%\nTotal: $2,018");
});

test("both halves of a neutral segment report the complete category even without labels", () => {
  const column = {name: "no", fmt: "num0", scale: {normalize: "percent"}, encodings:
    ["no", "neutral", "yes"].map(source => ({kind: "stacked_bar", source, diverge_at: "neutral"}))};
  const node = renderMarks(column, {no: 20, neutral: 30, yes: 50}, {min: -65, max: 65});
  const segments = [...node.querySelectorAll(".et-mark-stack-seg")];
  assert.deepEqual(inspectionData(segments[0]), inspectionData(segments[2]));
  assert.equal(tooltipText(inspectionData(segments[0])), "Neutral: 30.0%\nValue: 30\nTotal: 100");
});

test("density bands and IQR boxes describe the supplied support and whiskers", () => {
  const enc = {kind: "distribution", source: "density", distribution: {x: "x", y: "y", height: 0.5}};
  const node = renderMarks({name: "density", encodings: [enc]}, {density: [{x: 1, y: 0}, {x: 2, y: 3}, {x: 4, y: 0}]}, {min: 0, max: 5});
  assert.equal(tooltipText(inspectionData(node.querySelector(".et-mark-distribution"))),
    "Density: Density band\nSupport start: 1\nSupport end: 4\nPeak density: 3\nSamples: 3");
  const box = {kind: "boxplot", source: "median", whisker: "iqr", parts: {minimum: "lo", q1: "q1", median: "median", q3: "q3", maximum: "hi"}};
  const data = markTooltip({encodings: [box]}, box, {lo: 1, q1: 2, median: 3, q3: 4, hi: 5});
  assert.deepEqual(data.details.map(item => item.name), ["Lower whisker", "Lower quartile", "Median", "Upper quartile", "Upper whisker"]);
});

function fixture() {
  const root = document.createElement("div");
  root.innerHTML = "<table><tbody><tr><td></td></tr></tbody></table>";
  document.body.append(root);
  const cell = root.querySelector("td");
  for (const [name, x] of [["A", 40], ["B", 41], ["C", 90]]) {
    const node = inspectable(document.createElement("span"), {name, value: "20%", color: "red"}, {priority: 3});
    node.getBoundingClientRect = () => ({left: x, right: x + 8, top: 10, bottom: 18, width: 8, height: 8});
    cell.append(node);
  }
  inspectCell(cell, {name: "value"}, {}, {});
  return {root, cell};
}

test("overlapping point hit areas collect all values and ignore distant marks", () => {
  const {root, cell} = fixture();
  assert.deepEqual(hitTargets(cell, 38, 12).map(inspectionData).map(data => data.name), ["A", "B"]);
  assert.deepEqual(hitTargets(cell, 94, 12).map(inspectionData).map(data => data.name), ["C"]);
  assert.deepEqual(hitTargets(cell, 70, 12), []);
  assert.equal(cell.tabIndex, 0);
  assert.equal(cell.querySelectorAll("[tabindex]").length, 0);
  root.remove();
});

test("controller renders safe multiline content, cycles by keyboard and cleans up on rerender/destroy", () => {
  const {root, cell} = fixture();
  const controller = new TooltipController(root);
  controller.refresh();
  cell.dispatchEvent(new dom.window.FocusEvent("focusin", {bubbles: true}));
  assert.equal(controller.popup.hidden, false);
  assert.equal(controller.popup.querySelectorAll(".et-tooltip-entry").length, 2);
  assert.equal(cell.getAttribute("aria-describedby"), controller.popup.id);
  cell.dispatchEvent(new dom.window.KeyboardEvent("keydown", {key: "End", bubbles: true}));
  assert.equal(controller.popup.querySelector(".et-tooltip-name").textContent, "C:");
  cell.dispatchEvent(new dom.window.KeyboardEvent("keydown", {key: "ArrowRight", bubbles: true}));
  assert.equal(controller.popup.querySelectorAll(".et-tooltip-entry").length, 2);
  cell.dispatchEvent(new dom.window.KeyboardEvent("keydown", {key: "Escape", bubbles: true}));
  assert.equal(controller.popup.hidden, true);
  assert.equal(cell.hasAttribute("aria-describedby"), false);
  controller.showData([{value: "<img src=x onerror=bad()>\nSecond line"}], cell, 10, 10);
  assert.equal(controller.popup.querySelector("img"), null);
  assert.match(controller.popup.textContent, /\nSecond line/);
  controller.refresh();
  assert.equal(controller.popup.hidden, true);
  assert.equal(root.querySelectorAll("[data-et-tooltip][title]").length, 0);
  controller.destroy();
  assert.equal(root.querySelector(".et-tooltip"), null);
  root.remove();
});

test("cell overrides disable every child or replace them with literal/bound text", () => {
  for (const tooltip of [false, "One\nTwo", "@hint", "@missing"]) {
    const {root, cell} = fixture();
    inspectCell(cell, {name: "value", tooltip}, {hint: "Bound\nText"}, {});
    assert.equal(cell.querySelectorAll("[data-et-tooltip]").length, 0);
    // This helper normally receives a fresh cell, as in a real rerender.
    if (typeof tooltip === "string" && tooltip !== "@missing") {
      assert.equal(inspectionData(cell).value, tooltip === "@hint" ? "Bound\nText" : tooltip);
    }
    root.remove();
  }
});

test("sparklines inspect exactly one nearest x across their full height and use signed fill colors", () => {
  const cell = document.createElement("td");
  const svg = renderSparkline({sparkline_options: {type: "area", signed: true, reference: 1, color: "green", y_fmt: "pct0"}},
    [0.8, 1.2, 0.9]);
  cell.append(svg);
  svg.getBoundingClientRect = () => ({left: 0, right: 100, top: 0, bottom: 20});
  [...svg.querySelectorAll("circle")].forEach((node, index) => {
    node.getBoundingClientRect = () => ({left: 20 + index * 3, right: 24 + index * 3, top: 7, bottom: 12, width: 4, height: 5});
  });
  for (const y of [1, 10, 19]) {
    const values = hitTargets(cell, 25, y);
    assert.equal(values.length, 1);
    assert.equal(inspectionData(values[0]).value, "120%");
    assert.equal(inspectionData(values[0]).color, "green");
  }
  assert.match(inspectionData(hitTargets(cell, 21, 10)[0]).color, /--et-negative/);
});

test("hover delays survive pointer motion and are cancelled by leaving, refresh and destruction", t => {
  t.mock.timers.enable({apis: ["setTimeout"]});
  const {root, cell} = fixture();
  inspectCell(cell, {name: "value", tooltip_options: {text_delay: 1.5}}, {}, {});
  const controller = new TooltipController(root);
  const nodes = [...cell.querySelectorAll("[data-et-tooltip]")];
  controller.hover(nodes, cell, 40, 10);
  t.mock.timers.tick(1000);
  assert.equal(controller.popup.hidden, true);
  controller.hover(nodes, cell, 41, 10);
  t.mock.timers.tick(500);
  assert.equal(controller.popup.hidden, false);
  controller.hide();
  controller.hover(nodes, cell, 40, 10);
  controller.refresh();
  t.mock.timers.tick(2000);
  assert.equal(controller.popup.hidden, true);
  controller.hover(nodes, cell, 40, 10);
  controller.scheduleHide();
  t.mock.timers.tick(2000);
  assert.equal(controller.popup.hidden, true);
  controller.hover(nodes, cell, 40, 10);
  controller.destroy();
  t.mock.timers.tick(2000);
  assert.equal(root.querySelector(".et-tooltip"), null);
  root.remove();
});

test("overlapping values sort by their numeric x coordinate, with declaration-order ties", () => {
  const {root, cell} = fixture();
  const controller = new TooltipController(root);
  const nodes = [...cell.querySelectorAll("[data-et-tooltip]")];
  for (const [node, data] of nodes.map((node, i) => [node, {name: ["High", "Low", "Equal low"][i], xValue: [25.3, 23.9, 23.9][i], value: "formatted"}])) {
    inspectable(node, data, {priority: 3});
  }
  assert.deepEqual(controller.values(nodes).map(data => data.name), ["Low", "Equal low", "High"]);
  controller.destroy(); root.remove();
});

function denseFixture({column = {}, table = {}, coincident = false} = {}) {
  const root = document.createElement("div");
  root.innerHTML = '<table><tbody><tr><td><div class="et-marks"></div></td></tr></tbody></table>';
  document.body.append(root);
  const cell = root.querySelector("td"), track = cell.firstChild;
  const nodes = Array.from({length: 25}, (_, index) => {
    // A logarithmic projection: equal screen steps represent unequal values.
    const center = coincident ? 52 : 40 + index;
    const node = inspectable(document.createElement("span"),
      {name: `Point ${index}`, value: String(2 ** index), xValue: 2 ** index}, {priority: 3});
    node.getBoundingClientRect = () => ({left: center - 5, right: center + 5, top: 9, bottom: 19, width: 10, height: 10});
    track.append(node);
    return node;
  });
  inspectCell(cell, {name: "samples", ...column}, {}, table);
  const controller = new TooltipController(root);
  return {root, cell, nodes, controller};
}

test("dense point tooltips default to the 10 nearest screen positions and follow the pointer", () => {
  const {root, cell, controller} = denseFixture();
  controller.hover(hitTargets(cell, 52, 14), cell, 52, 14);
  assert.equal(controller.popup.querySelectorAll(".et-tooltip-entry").length, 10);
  assert.deepEqual([...controller.popup.querySelectorAll(".et-tooltip-name")].map(node => node.textContent),
    Array.from({length: 10}, (_, index) => `Point ${index + 7}:`));
  controller.hover(hitTargets(cell, 58, 14), cell, 58, 14);
  assert.deepEqual([...controller.popup.querySelectorAll(".et-tooltip-name")].map(node => node.textContent),
    Array.from({length: 10}, (_, index) => `Point ${index + 13}:`));
  assert.equal(cell.querySelectorAll("[data-et-tooltip]").length, 25);
  controller.destroy(); root.remove();
});

test("table limits apply to points and column overrides win, including a limit of one", () => {
  for (const [column, table, count] of [
    [{}, {tooltips: {max_entries: 12}}, 12],
    [{tooltip_options: {max_entries: 4}}, {tooltips: {max_entries: 12}}, 4],
    [{tooltip_options: {max_entries: 1}}, {}, 1],
    [{tooltip_options: {max_entries: 40}}, {}, 21],
  ]) {
    const {root, cell, controller} = denseFixture({column, table});
    controller.hover(hitTargets(cell, 52, 14), cell, 52, 14);
    assert.equal(controller.popup.querySelectorAll(".et-tooltip-entry").length, count);
    controller.destroy(); root.remove();
  }
});

test("deduplicating values does not use up the nearest-point allowance", () => {
  const {root, cell, nodes, controller} = denseFixture({column: {tooltip_options: {max_entries: 3}}});
  for (const node of nodes.slice(8, 14)) inspectable(node, {name: "Repeated", value: "value", xValue: 10}, {priority: 3});
  const selected = controller.values(hitTargets(cell, 52, 14), cell, 52, 14);
  assert.equal(selected.length, 3);
  assert.equal(selected.filter(data => data.name === "Repeated").length, 1);
  assert.deepEqual(selected.map(data => data.name), ["Repeated", "Point 14", "Point 15"]);
  controller.destroy(); root.remove();
});

test("keyboard inspection keeps the focused point in a capped coincident group", () => {
  const {root, cell, controller} = denseFixture({column: {tooltip_options: {max_entries: 3}}, coincident: true});
  cell.dispatchEvent(new dom.window.FocusEvent("focusin", {bubbles: true}));
  assert.equal(controller.popup.querySelectorAll(".et-tooltip-entry").length, 3);
  cell.dispatchEvent(new dom.window.KeyboardEvent("keydown", {key: "End", bubbles: true}));
  assert.deepEqual([...controller.popup.querySelectorAll(".et-tooltip-name")].map(node => node.textContent),
    ["Point 0:", "Point 1:", "Point 24:"]);
  controller.destroy(); root.remove();
});

test("touch snapshots use the nearest-point limit before a row can be replaced", t => {
  t.mock.timers.enable({apis: ["setTimeout"]});
  const {root, cell, nodes, controller} = denseFixture({column: {tooltip_options: {max_entries: 3}}});
  const event = new dom.window.MouseEvent("pointerup", {bubbles: true, clientX: 52, clientY: 14});
  Object.defineProperty(event, "pointerType", {value: "touch"});
  nodes[12].dispatchEvent(event);
  cell.addEventListener("click", () => { controller.refresh(); cell.replaceChildren(); });
  nodes[12].dispatchEvent(new dom.window.MouseEvent("click", {bubbles: true}));
  t.mock.timers.tick(1);
  assert.deepEqual([...controller.popup.querySelectorAll(".et-tooltip-name")].map(node => node.textContent),
    ["Point 11:", "Point 12:", "Point 13:"]);
  controller.destroy(); root.remove();
});

test("touch pointerleave does not dismiss inspection like a mouse hover", t => {
  t.mock.timers.enable({apis: ["setTimeout"]});
  const {root, cell} = fixture();
  const controller = new TooltipController(root);
  controller.showData([{name: "Value", value: "12"}], cell, 40, 10);
  const touchLeave = new dom.window.Event("pointerleave");
  Object.defineProperty(touchLeave, "pointerType", {value: "touch"});
  root.dispatchEvent(touchLeave);
  t.mock.timers.tick(500);
  assert.equal(controller.popup.hidden, false);
  root.dispatchEvent(new dom.window.Event("pointerleave"));
  t.mock.timers.tick(150);
  assert.equal(controller.popup.hidden, true);
  controller.destroy(); root.remove();
});

test("touch inspection waits for the click and survives a row replacement after pointerup", t => {
  t.mock.timers.enable({apis: ["setTimeout"]});
  const {root, cell} = fixture();
  const controller = new TooltipController(root);
  const point = cell.querySelector("[data-et-tooltip]");
  const event = new dom.window.MouseEvent("pointerup", {bubbles: true, clientX: 44, clientY: 14});
  Object.defineProperty(event, "pointerType", {value: "touch"});
  point.dispatchEvent(event);
  t.mock.timers.tick(300);
  assert.equal(controller.popup.hidden, true);
  cell.addEventListener("click", () => { controller.refresh(); cell.replaceChildren(); });
  point.dispatchEvent(new dom.window.MouseEvent("click", {bubbles: true}));
  t.mock.timers.tick(1);
  assert.equal(controller.popup.hidden, false);
  assert.equal(controller.popup.querySelectorAll(".et-tooltip-entry").length, 2);
  controller.destroy(); root.remove();
});
