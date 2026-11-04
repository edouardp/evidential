import {test} from "node:test";
import assert from "node:assert/strict";
import {benchmarkLayoutProjection} from "./benchmark.js";

test("projection benchmark reports preparation separately and labels excluded browser work", () => {
  const report = benchmarkLayoutProjection([1, 21, 100], 2);
  assert.deepEqual(report.results.map(result => result.rows), [1, 21, 100]);
  assert.match(report.environment, /DOM\/layout\/paint excluded/);
  for (const result of report.results) {
    assert.ok(Number.isFinite(result.initial_ms) && result.initial_ms >= 0);
    assert.ok(Number.isFinite(result.navigation_ms) && result.navigation_ms >= 0);
  }
});

test("projection benchmark rejects invalid scenarios before allocating datasets", () => {
  for (const counts of [[], [0], [-1], [1.5]]) assert.throws(() => benchmarkLayoutProjection(counts), /positive integers/);
  assert.throws(() => benchmarkLayoutProjection([10], 0), /positive integers/);
});
