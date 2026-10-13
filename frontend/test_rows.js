import { test } from "node:test";
import assert from "node:assert/strict";
import { sortRows, searchRows, visibleRows, paginateRows, columnStats } from "./src/rows.js";

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
  assert.deepEqual(columnStats(columns, rows).get("x"), { min: 1, max: 2, avg: 1.5, nulls: 0, distinct: 2 });
});

test("pagination clamps stale pages when results shrink", () => {
  const rows = [{ x: 1 }, { x: 2 }, { x: 3 }];
  assert.deepEqual(paginateRows(rows, 2, 99, {}), { rows: [rows[2]], pageCount: 2, page: 1, total: 3 });
  assert.equal(paginateRows(rows, "all", 99, {}).rows, rows);
});
