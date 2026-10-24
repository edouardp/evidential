import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import { isFlexibleChart, renderColumnSizing } from "./src/column-sizing.js";

const dom = new JSDOM("<!DOCTYPE html>");
global.document = dom.window.document;
global.Node = dom.window.Node;

test("only graphics that use the available cell width grow", () => {
  for (const kind of ["bar", "point", "points", "range", "stacked_bar", "strip", "boxplot", "distribution"]) {
    assert.equal(isFlexibleChart({encodings: [{kind}]}), true);
  }
  assert.equal(isFlexibleChart({viz: "bar"}), true);
  for (const column of [{}, {encodings: []}, {viz: "sparkline"}, {viz: "chip"}, {viz: "color"}, {viz: "symbols"}]) {
    assert.equal(isFlexibleChart(column), false);
  }
});

test("tables without flexible charts retain the browser's content sizing", () => {
  assert.equal(renderColumnSizing([{name: "team"}, {name: "wins", type: "number"}]), null);
  assert.equal(renderColumnSizing([]), null);
});

test("sizing describes physical columns, including utility and sub-columns", () => {
  const columns = [
    {name: "question", column_group: ["Survey", "Question"]},
    {name: "count", subcolumn_group: "Sample"},
    {name: "period", subcolumn_group: "Sample"},
    {name: "response", encodings: [{kind: "stacked_bar"}]},
    {name: "trend", viz: "sparkline", sparkline_options: {width: 96}},
  ];
  const sizing = renderColumnSizing(columns, {rowNumbers: true, link: true});
  assert.equal(sizing.tagName, "COLGROUP");
  assert.deepEqual([...sizing.children].map(col => col.className), [
    "et-col-content", "et-col-content", "et-col-content", "et-col-content",
    "et-col-chart", "et-col-content", "et-col-content",
  ]);
  assert.equal(renderColumnSizing(columns).children.length, columns.length);
});
