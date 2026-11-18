import {test} from "node:test";
import assert from "node:assert/strict";
import {buildHeaderLevels, headerLayout, orderedColumns} from "./src/headers.js";

const columns = [
  {name: "country"},
  {name: "value", column_group: ["Economy", "GDP"], subcolumn_group: "Latest"},
  {name: "forecast", column_group: ["Economy", "GDP"]},
  {name: "period", column_group: ["Economy", "GDP"], subcolumn_group: "Latest"},
  {name: "status", column_group: ["Economy", "GDP"], subcolumn_group: "Latest"},
  {name: "inflation", column_group: ["Economy", "Prices"], subcolumn_group: "Latest"},
  {name: "month", column_group: ["Economy", "Prices"], subcolumn_group: "Latest"},
];

test("a run of ungrouped columns is split at the freeze boundary", () => {
  const paths = [[], [], [], [], ["Spend"], ["Spend"], []];
  assert.deepEqual(buildHeaderLevels(paths, 1, 1)[0], [
    {label: "", span: 1, start: 0},
    {label: "", span: 3, start: 1},
    {label: "Spend", span: 2, start: 4},
    {label: "", span: 1, start: 6},
  ]);
  // Named groups are never split; no boundary keeps today's layout.
  assert.deepEqual(buildHeaderLevels([["A"], ["A"]], 1, 1)[0], [{label: "A", span: 2, start: 0}]);
  assert.equal(buildHeaderLevels(paths, 1)[0].length, 3);
});

test("nested blank spanners split without splitting their named parent", () => {
  const grouped = [
    {name: "a", column_group: ["A"]},
    {name: "b", column_group: ["A"]},
    {name: "c", column_group: ["A", "B"]},
  ];
  const layout = headerLayout(grouped, {breakAt: 1});
  assert.deepEqual(layout.levels, [
    [{label: "A", span: 3, start: 0}],
    [{label: "", span: 1, start: 0}, {label: "", span: 1, start: 1}, {label: "B", span: 1, start: 2}],
  ]);
  for (const breakAt of [0, 3, 4]) {
    assert.deepEqual(headerLayout(grouped, {breakAt}), headerLayout(grouped));
  }
});

test("two frozen ungrouped columns share a blank spanner at each depth", () => {
  const paths = [[], [], [], ["Spend", "Daily"], ["Spend", "Daily"], ["Spend", "Budget"]];
  const blanks = [{label: "", span: 2, start: 0}, {label: "", span: 1, start: 2}];
  assert.deepEqual(buildHeaderLevels(paths, 2, 2), [
    [...blanks, {label: "Spend", span: 3, start: 3}],
    [...blanks, {label: "Daily", span: 2, start: 3}, {label: "Budget", span: 1, start: 5}],
  ]);
});

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
