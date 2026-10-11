import { test } from "node:test";
import assert from "node:assert/strict";
import { formatValue, formatTitle } from "./src/format.js";

test("numeric formats", () => {
  assert.equal(formatValue(1234.5, "num2"), "1,234.50");
  assert.equal(formatValue(1234.5, "usd0"), "$1,235");
  assert.equal(formatValue(1234.5, "usd2"), "$1,234.50");
  assert.equal(formatValue(0.1234, "pct1"), "12.3%");
  assert.equal(formatValue(42, "id"), "42");
});

test("auto-scaled base formats", () => {
  assert.equal(formatValue(2400, "num", { range: { min: 0, max: 5000 } }), "2k");
  assert.equal(formatValue(1_500_000, "usd", { range: { min: 0, max: 2_000_000 } }), "$1.5M");
  assert.equal(formatValue(0, "usd"), "$0");
});

test("date formats", () => {
  const d = new Date(2024, 2, 15);
  assert.equal(formatValue(d, "date"), "2024-03-15");
  assert.equal(formatValue(d, "mmm"), "Mar");
  assert.equal(formatValue(d, "yyyy"), "2024");
  assert.equal(formatValue(d, "quarter"), "2024-Q1");
  assert.equal(formatValue(new Date(2024, 4, 1), "qq"), "Q2");
});

test("nulls and fallbacks", () => {
  assert.equal(formatValue(null, "num"), "–");
  assert.equal(formatValue(undefined, "usd", { fallback: "-" }), "-");
});

test("titles", () => {
  assert.equal(formatTitle("total_revenue"), "Total Revenue");
  assert.equal(formatTitle("sum(trip_distance)"), "Sum(Trip Distance)");
});
