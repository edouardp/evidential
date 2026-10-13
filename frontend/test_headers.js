import {test} from "node:test";
import assert from "node:assert/strict";
import {headerLayout, orderedColumns} from "./src/headers.js";

const columns = [
  {name: "country"},
  {name: "value", column_group: ["Economy", "GDP"], subcolumn_group: "Latest"},
  {name: "forecast", column_group: ["Economy", "GDP"]},
  {name: "period", column_group: ["Economy", "GDP"], subcolumn_group: "Latest"},
  {name: "status", column_group: ["Economy", "GDP"], subcolumn_group: "Latest"},
  {name: "inflation", column_group: ["Economy", "Prices"], subcolumn_group: "Latest"},
  {name: "month", column_group: ["Economy", "Prices"], subcolumn_group: "Latest"},
];

test("sub-columns cluster stably within the full parent path without mutating input", () => {
  const input = Object.freeze(columns.map((column) => Object.freeze({...column})));
  const ordered = orderedColumns(input, {});
  assert.deepEqual(ordered.map((col) => col.name), ["country", "value", "period", "status", "forecast", "inflation", "month"]);
  const layout = headerLayout(ordered);
  assert.equal(layout.depth, 2);
  assert.deepEqual(layout.leaves, [
    {start: 0, span: 1, label: null},
    {start: 1, span: 3, label: "Latest"},
    {start: 4, span: 1, label: null},
    {start: 5, span: 2, label: "Latest"},
  ]);
  assert.deepEqual(layout.joins.get("period"), {left: true, right: true, label: "Latest"});
  assert.deepEqual(layout.levels[1].map((cell) => cell.span), [1, 4, 2]);
});

test("unclustered nonadjacent sub-columns and different parents never merge", () => {
  assert.equal(orderedColumns(columns, {order_columns_by_group: false}), columns);
  const layout = headerLayout(columns);
  assert.deepEqual(layout.leaves.map((leaf) => leaf.span), [1, 1, 1, 2, 2]);
  const different = headerLayout([
    {name: "a", column_group: "One", subcolumn_group: "Latest"},
    {name: "b", column_group: "Two", subcolumn_group: "Latest"},
  ]);
  assert.deepEqual(different.leaves.map((leaf) => leaf.span), [1, 1]);
});

test("hidden members and singleton groups recompute spans and outer padding", () => {
  const ordered = orderedColumns(columns.filter((col) => !["period", "forecast"].includes(col.name)), {});
  const layout = headerLayout(ordered);
  assert.equal(layout.leaves[1].span, 2);
  assert.deepEqual(layout.joins.get("value"), {left: false, right: true, label: "Latest"});
  assert.deepEqual(layout.joins.get("status"), {left: true, right: false, label: "Latest"});
  const singleton = headerLayout([{name: "value", subcolumn_group: "Latest"}]);
  assert.equal(singleton.leaves[0].label, "Latest");
  assert.equal(singleton.joins.size, 0);
  assert.deepEqual(headerLayout([]).leaves, []);
});
