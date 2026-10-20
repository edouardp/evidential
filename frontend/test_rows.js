import { test } from "node:test";
import assert from "node:assert/strict";
import { sortRows, searchRows, visibleRows, paginateRows, columnStats, withDecimals, sectionContinuation } from "./src/rows.js";
import { RowPipeline } from "./src/derived.js";

test("withDecimals keeps an explicit precision and pads an auto base", () => {
  // An explicit precision is already aligned: keep it.
  assert.equal(withDecimals("pct1", 4), "pct1");
  assert.equal(withDecimals("num0", 3), "num0");
  assert.equal(withDecimals("usd2", 1), "usd2");
  // An auto base is padded to the observed precision.
  assert.equal(withDecimals("num", 2), "num2");
  assert.equal(withDecimals("usd", 3), "usd3");
  // A percent base shows value*100, so two fewer rendered places.
  assert.equal(withDecimals("pct", 4), "pct2");
  assert.equal(withDecimals("pct", 1), "pct0");
  // Unknown codes are left alone.
  assert.equal(withDecimals("id", 0), "id");
  assert.equal(withDecimals("num0k", 2), "num0k");
});

test("row pipeline preserves grouping and never mutates its inputs", () => {
  const rows = Object.freeze([
    Object.freeze({ x: 1, name: "match", __parent_key: "A", __ancestors: ["A"] }),
    Object.freeze({ x: 2, name: "other", __parent_key: "A", __ancestors: ["A"] }),
    Object.freeze({ x: 3, render_type: "row_subtotal", __group_key: "A" }),
    Object.freeze({ x: 3, render_type: "row_total" }),
  ]);
  const columns = [{ name: "x", type: "number" }, { name: "name" }];
  assert.deepEqual(sortRows(rows, columns, { column: "x", direction: "desc" }),
    [rows[1], rows[0], rows[2], rows[3]]);
  const searched = searchRows(rows, columns, "match", new Set());
  assert.deepEqual(searched, [rows[0], rows[2], rows[3]]);
  assert.deepEqual(visibleRows(searched, () => true), [rows[2], rows[3]]);
  assert.deepEqual(columnStats(columns, rows).get("x"),
    { min: 1, max: 2, avg: 1.5, nulls: 0, distinct: 2, trues: 0, falses: 0 });
});

test("pagination clamps stale pages when results shrink", () => {
  const rows = [{ x: 1 }, { x: 2 }, { x: 3 }];
  assert.deepEqual(paginateRows(rows, 2, 99, {}), {
    rows: [rows[2]], pageCount: 2, page: 1, total: 3, start: 2,
  });
  assert.equal(paginateRows(rows, "all", 99, {}).rows, rows);
});

test("section rows paginate and repeat their label as a continuation", () => {
  const rows = [
    { render_type: "row_section", __label: "North" },
    { x: 1 }, { x: 2 },
    { render_type: "row_section", __label: "South" },
    { x: 3 }, { x: 4 },
  ];
  const page = paginateRows(rows, 4, 1, {});
  assert.equal(page.pageCount, 2);
  assert.equal(page.start, 4);
  assert.equal(sectionContinuation(rows, page.start, page.rows), "South (cont.)");
  // The first page starts with its own section row: no continuation needed.
  assert.equal(sectionContinuation(rows, 0, rows.slice(0, 4)), null);
});

test("derived data invalidates search, sort, hidden columns and group visibility independently", () => {
  const pipeline = new RowPipeline();
  const inputs = {
    rows: [
      {x: 1, name: "match", __ancestors: ["A"]},
      {x: 3, name: "other", __ancestors: ["A"]},
      {x: 4, render_type: "row_subtotal", __group_key: "A"},
    ],
    columns: [{name: "x", type: "number", viz: "color"}, {name: "name"}],
    options: {column_stats: true}, search: "", hidden: new Set(), sort: null,
  };
  const first = pipeline.get(inputs);
  assert.equal(pipeline.get({...inputs, hidden: new Set()}), first);
  assert.equal(first.stats.get("x").avg, 2);
  const open = pipeline.visible(first, 0, () => false);
  assert.equal(open.rows.length, 3);
  assert.equal(pipeline.visible(first, 1, () => true).rows.length, 1);
  const searched = pipeline.get({...inputs, search: "match"});
  assert.deepEqual(searched.sorted.map((row) => row.x), [1, 4]);
  assert.deepEqual(searched.ranges.get("x"), {min: 1, max: 4});
  const sorted = pipeline.get({...inputs, sort: {column: "x", direction: "desc"}});
  assert.deepEqual(sorted.sorted.map((row) => row.x), [3, 1, 4]);
  const hidden = pipeline.get({...inputs, hidden: new Set(["x"])});
  assert.deepEqual(hidden.columns.map((column) => column.name), ["name"]);
  pipeline.clear();
  inputs.rows[0].x = 10;
  assert.equal(pipeline.get(inputs).stats.get("x").avg, 6.5);
});
