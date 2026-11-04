import {test} from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {aggregateValues} from "./src/aggregates.js";
import {summaryValue} from "./src/row-layout.js";

const cases = JSON.parse(readFileSync(new URL("../tests/fixtures/summary-contract.json", import.meta.url)));
for (const [index, entry] of cases.entries()) test(`shared summary contract ${index}: ${entry.operation}`, () => {
  assert.deepEqual(aggregateValues(entry.operation, entry.values), entry.expected);
  assert.deepEqual(summaryValue({operation: entry.operation, source: "value"}, entry.values.map(value => ({value}))), entry.expected);
});
test("invalid mixed-type numeric summaries fail explicitly", () => {
  assert.throws(() => aggregateValues("sum", [1, "2"]), TypeError);
  assert.throws(() => aggregateValues("invalid", [1]), TypeError);
});
