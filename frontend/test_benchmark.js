import { test } from "node:test";
import assert from "node:assert/strict";
import { benchmarkRenderer, median } from "./benchmark.js";

test("benchmark reports real rendering scenarios and handles sample medians", () => {
  const values = [9, 1, 5, 3];
  assert.equal(median(values), 4);
  assert.deepEqual(values, [9, 1, 5, 3]);
  assert.equal(median([9, 1, 5]), 5);
  const report = benchmarkRenderer([8], 2);
  assert.equal(report.results[0].rows, 8);
  assert.equal(report.results[0].columns, 8);
  assert.ok(report.results[0].initial_ms > 0);
  assert.equal(document.body.childElementCount, 0);
  assert.throws(() => benchmarkRenderer([0]), /positive/);
});
