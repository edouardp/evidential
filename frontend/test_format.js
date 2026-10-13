import { test } from "node:test";
import assert from "node:assert/strict";
import { formatValue, formatRelative, formatTitle } from "./src/format.js";

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

test("datetime preset", () => {
  const d = new Date(2024, 2, 15, 13, 4, 5);
  assert.equal(formatValue(d, "datetime"), "2024-03-15 13:04:05");
});

test("relative time", () => {
  const now = Date.UTC(2024, 2, 15, 12, 0, 0);
  assert.equal(formatRelative("2024-03-12T12:00:00Z", true, now), "3 days ago");
  assert.equal(formatRelative("2024-03-18T12:00:00Z", true, now), "in 3 days");
  assert.equal(formatRelative("2024-03-15T14:00:00Z", true, now), "in 2 hours");
  assert.equal(formatRelative("2024-03-15T10:00:00Z", "hour", now), "2 hours ago");
  assert.equal(formatRelative("2024-03-15T10:30:00Z", "minute", now), "90 minutes ago");
  assert.equal(formatRelative("not a date", true, now), null);
});

test("formatValue renders relative when asked", () => {
  const now = Date.UTC(2024, 2, 15, 12, 0, 0);
  assert.equal(formatValue("2024-03-12T12:00:00Z", "date", { type: "date", relative: true, now }), "3 days ago");
  // An unparseable value falls back to the absolute format.
  assert.equal(formatValue("n/a", "date", { type: "date", relative: true, now }), "n/a");
});

test("nulls and fallbacks", () => {
  assert.equal(formatValue(null, "num"), "–");
  assert.equal(formatValue(undefined, "usd", { fallback: "-" }), "-");
});

test("special formatters (bytes, duration, roman, flag)", () => {
  assert.equal(formatValue(1536, "bytes"), "1.50 KB");
  assert.equal(formatValue(90000, "duration"), "1d 1h");
  assert.equal(formatValue(2024, "roman"), "MMXXIV");
  assert.equal(formatValue("AU", "flag"), "\u{1F1E6}\u{1F1FA}");
  // ISO 3166-1 alpha-3 codes render the same flag as their alpha-2 form.
  assert.equal(formatValue("NZL", "flag"), "\u{1F1F3}\u{1F1FF}");
  assert.equal(formatValue("JPN", "flag"), "\u{1F1EF}\u{1F1F5}");
  assert.equal(formatValue("usa", "flag"), "\u{1F1FA}\u{1F1F8}");
  assert.equal(formatValue("ZZZ", "flag"), "ZZZ");
});

test("titles", () => {
  assert.equal(formatTitle("total_revenue"), "Total Revenue");
  assert.equal(formatTitle("sum(trip_distance)"), "Sum(Trip Distance)");
});

test("numeric columns preserve textual missing-value labels instead of displaying NaN", () => {
  assert.equal(formatValue("nil", "num1", {type: "number"}), "nil");
  assert.equal(formatValue("na", "num1", {type: "number", fallback: "Unavailable"}), "Unavailable");
  assert.equal(formatValue("2.9", "num1", {type: "number"}), "2.9");
});
