import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import { renderMarkLabel, fitMarkLabels } from "./src/mark-labels.js";

global.document = new JSDOM("<!doctype html><body></body>").window.document;
global.Node = document.defaultView.Node;

function fixture({position = "outside_end", left = 0, width = 90, negative = false, textWidth = 20, ...options} = {}) {
  const table = document.createElement("table");
  const cell = table.insertRow().insertCell();
  let cellWidth = 100;
  const label = renderMarkLabel({}, {kind: "bar", source: "x", label: {value: true, position, auto: true, ...options}},
    {x: 123}, {leftPct: left, widthPct: width, negative, color: "#111111"});
  cell.append(label);
  cell.getBoundingClientRect = () => ({left: 0, right: cellWidth, width: cellWidth});
  label.firstChild.getBoundingClientRect = () => ({width: textWidth});
  label.getBoundingClientRect = () => {
    if (label.hidden) return {left: 0, right: 0, width: 0};
    const x = parseFloat(label.style.left) * cellWidth / 100;
    const inside = label.classList.contains("et-mark-label-inside");
    const boxWidth = inside ? parseFloat(label.style.width) * cellWidth / 100 : textWidth + 6;
    const boxLeft = inside ? x : label.classList.contains("et-mark-label-left") ? x - boxWidth - 3 : x + 3;
    return {left: boxLeft, right: boxLeft + boxWidth, width: boxWidth};
  };
  return {table, label, resize: width => { cellWidth = width; }, fit: () => fitMarkLabels(table)};
}

test("fixed labels that do not fit leave layout and reappear after resizing", () => {
  const testCase = fixture({auto: false, width: 80});
  testCase.fit();
  assert.equal(testCase.label.style.visibility, "hidden");
  assert.equal(testCase.label.hidden, true);
  assert.equal(testCase.label.title, "123");
  testCase.resize(300);
  testCase.fit();
  assert.equal(testCase.label.style.visibility, "");
  assert.equal(testCase.label.hidden, false);
  assert.equal(testCase.label.dataset.labelPosition, "outside_end");
});

test("fixed labels with explicit overflow remain visible beyond the cell", () => {
  const testCase = fixture({auto: false, width: 100, overflow: "show"});
  testCase.fit();
  assert.equal(testCase.label.style.visibility, "");
  assert.equal(testCase.label.hidden, false);
});

test("automatic labels try both sides of the requested start or end, in preferred order", () => {
  for (const position of ["outside_start", "outside_end", "inside_start", "inside_end"]) {
    const testCase = fixture({position, left: 10, width: 80});
    testCase.fit();
    assert.equal(testCase.label.dataset.labelPosition, position.replace("outside", "inside"));
    assert.equal(testCase.label.style.visibility, "");
  }
  const outside = fixture({width: 30});
  outside.fit();
  assert.equal(outside.label.dataset.labelPosition, "outside_end");
  const inside = fixture({position: "inside_end", width: 30});
  inside.fit();
  assert.equal(inside.label.dataset.labelPosition, "inside_end");
  const small = fixture({position: "inside_start", width: 10, left: 50});
  small.fit();
  assert.equal(small.label.dataset.labelPosition, "outside_start");
});

test("negative bar labels retain their numeric start/end when moving inside", () => {
  for (const [position, expectedAlignment] of [["outside_end", "begin"], ["outside_start", "end"]]) {
    const testCase = fixture({position, left: 10, width: 80, negative: true});
    testCase.fit();
    assert.equal(testCase.label.dataset.labelPosition, position.replace("outside", "inside"));
    assert.ok(testCase.label.classList.contains(`et-mark-label-align-${expectedAlignment}`));
  }
});

test("automatic placement reverses on resize and clears automatic inside contrast outside", () => {
  const testCase = fixture({width: 80});
  testCase.fit();
  assert.equal(testCase.label.dataset.labelPosition, "inside_end");
  assert.equal(testCase.label.style.color, "rgb(255, 255, 255)");
  testCase.resize(300);
  testCase.fit();
  assert.equal(testCase.label.dataset.labelPosition, "outside_end");
  assert.equal(testCase.label.style.color, "");
  assert.equal(testCase.label.dataset.autoContrast, undefined);
  testCase.resize(100);
  testCase.fit();
  assert.equal(testCase.label.dataset.labelPosition, "inside_end");
});

test("labels omitted when neither side fits reappear when space returns", () => {
  const testCase = fixture({width: 50});
  testCase.resize(30);
  testCase.fit();
  assert.equal(testCase.label.style.visibility, "hidden");
  assert.equal(testCase.label.hidden, true);
  assert.equal(testCase.label.title, "123");
  testCase.resize(100);
  testCase.fit();
  assert.equal(testCase.label.style.visibility, "");
  assert.equal(testCase.label.hidden, false);
  assert.equal(testCase.label.dataset.labelPosition, "outside_end");
});

test("zero-width inside labels try their outside counterpart", () => {
  for (const position of ["inside_start", "inside_end"]) {
    const testCase = fixture({position, width: 0, left: 50});
    testCase.fit();
    assert.equal(testCase.label.dataset.labelPosition, position.replace("inside", "outside"));
    assert.equal(testCase.label.style.visibility, "");
  }
});

test("explicit colors and minimum-width settings survive automatic placement", () => {
  const explicit = fixture({color: "yellow"});
  explicit.fit();
  assert.equal(explicit.label.style.color, "yellow");
  explicit.resize(500);
  explicit.fit();
  assert.equal(explicit.label.style.color, "yellow");
  const minimum = fixture({min_width: 95});
  minimum.fit();
  assert.equal(minimum.label.style.visibility, "hidden");
});

test("label typography is shared by bar, point and stacked labels", async () => {
  const {renderMarks} = await import("./src/visualizations.js");
  const spec = {value: true, format: "num0", font_weight: "600", font_style: "italic",
    font: "monospace", figure_style: "proportional", color: "black", position: "inside_end"};
  for (const kind of ["bar", "point", "stacked_bar"]) {
    const node = renderMarks({encodings: [{kind, source: "x", color: "#111111", label: spec}]}, {x: 1000}, {min: 0, max: 1000});
    const label = node.querySelector("[data-mark-label]");
    assert.equal(label.textContent, "1,000");
    assert.equal(label.style.fontWeight, "600");
    assert.equal(label.style.fontStyle, "italic");
    assert.equal(label.style.fontFamily, "monospace");
    assert.equal(label.style.fontVariantNumeric, "lining-nums proportional-nums");
    assert.equal(label.style.color, "black");
    assert.equal(label.dataset.autoContrast, undefined);
  }
});

test("automatic fitting retains font styles when changing sides", () => {
  const testCase = fixture({font_weight: "600", font_style: "italic", font: "monospace", textWidth: 30, width: 80});
  testCase.fit();
  assert.equal(testCase.label.dataset.labelPosition, "inside_end");
  testCase.resize(400);
  testCase.fit();
  assert.equal(testCase.label.dataset.labelPosition, "outside_end");
  assert.equal(testCase.label.style.fontWeight, "600");
  assert.equal(testCase.label.style.fontStyle, "italic");
  assert.equal(testCase.label.style.fontFamily, "monospace");
});
