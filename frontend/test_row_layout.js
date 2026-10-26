import { test } from "node:test";
import assert from "node:assert/strict";
import { projectLayout, projectLegacy, summaryValue } from "./src/row-layout.js";
import { RowPipeline } from "./src/derived.js";

const sum = {operation: "sum", source: "value"};
const count = {operation: "count", source: null, suffix: " products", format: "num0"};
const heading = label => ({label, align: "left", cells: {value: sum, name: count}});
const summary = {label: "Subtotal", cells: {value: sum}, position: "bottom"};
const grand = {label: "Total", cells: {value: sum}};
const source = [Object.freeze({name: "A", value: 10}), Object.freeze({name: "B", value: 30}), Object.freeze({name: "C", value: 100})];
const layout = {version: 1, groups: [
  {id: "north", members: [0, 1], depth: 0, children: [], section: heading("North"), summary},
  {id: "south", members: [2], depth: 0, children: [], section: heading("South"), summary},
], grand_summary: grand};

test("pagination counts detail records and keeps summaries with their final member", () => {
  const first = projectLayout(layout, source, source, 1, 0);
  assert.equal(first.total, 3);
  assert.equal(first.pageCount, 3);
  assert.deepEqual(first.entries.map(entry => entry.kind), ["section", "data"]);
  assert.equal(first.entries[0].cells.name.value, "2 products");
  const second = projectLayout(layout, source, source, 1, 1);
  assert.deepEqual(second.entries.map(entry => entry.kind), ["section", "data", "summary"]);
  assert.equal(second.entries[0].label, "North (cont.)");
  assert.deepEqual(second.entries[0].cells, {});
  assert.equal(second.entries[2].cells.value.value, 40);
  const last = projectLayout(layout, source, source, 1, 2);
  assert.deepEqual(last.entries.map(entry => entry.kind), ["section", "data", "summary", "grand_summary"]);
  assert.equal(last.entries[0].label, "South");
  assert.equal(last.entries.at(-1).cells.value.value, 140);
});

test("filtering recomputes named summaries and counts without including other summaries", () => {
  const found = projectLayout(layout, source, [source[1]], 2, 10);
  assert.equal(found.page, 0);
  assert.equal(found.total, 1);
  assert.equal(found.entries[0].cells.name.value, "1 products");
  assert.equal(found.entries[0].cells.value.value, 30);
  assert.equal(found.entries.at(-1).cells.value.value, 30);
  assert.ok(!found.entries.some(entry => entry.label === "South"));
  assert.equal(projectLayout(layout, source, [], 1, 0).entries.length, 0);
});

test("sorting changes detail order within groups, without moving records between them", () => {
  const page = projectLayout(layout, source, [source[2], source[1], source[0]], 0, 0);
  assert.deepEqual(page.entries.filter(entry => entry.kind === "data").map(entry => entry.row.name), ["B", "A", "C"]);
  assert.equal(page.entries[1].row, source[1]);
  assert.deepEqual(source[0], {name: "A", value: 10});
});

test("nested groups repeat ancestor context and emit each summary only once", () => {
  const nested = {version: 1, groups: [{id: "root", members: [0, 1, 2], depth: 0, section: heading("Root"), summary,
    children: layout.groups.map(group => ({...group, depth: 1}))}], grand_summary: grand};
  const middle = projectLayout(nested, source, source, 1, 1);
  assert.deepEqual(middle.entries.filter(entry => entry.kind === "section").map(entry => entry.label), ["Root (cont.)", "North (cont.)"]);
  assert.equal(middle.entries.filter(entry => entry.kind === "summary").length, 1);
  const last = projectLayout(nested, source, source, 1, 2);
  assert.equal(last.entries.filter(entry => entry.kind === "summary").length, 2);
  assert.equal(last.entries.filter(entry => entry.kind === "grand_summary").length, 1);
});

test("top summaries appear on the group's first page and optional annotations stay optional", () => {
  const top = {version: 1, groups: [{...layout.groups[0], summary: {...summary, position: "top"}}]};
  assert.deepEqual(projectLayout(top, source, source, 1, 0).entries.map(entry => entry.kind), ["section", "summary", "data"]);
  assert.deepEqual(projectLayout(top, source, source, 1, 1).entries.map(entry => entry.kind), ["section", "data"]);
  const plain = {version: 1, groups: [{id: "n", members: [0, 1], depth: 0, children: []}]};
  assert.ok(projectLayout(plain, source, source, 0, 0).entries.every(entry => entry.kind === "data"));
});

test("top summaries indent detail labels even without a separate section heading", () => {
  const top = {version: 1, groups: [{...layout.groups[0], section: undefined,
    summary: {...summary, position: "top"}}]};
  const page = projectLayout(top, source, source, 0, 0);
  assert.ok(page.entries.filter(entry => entry.kind === "data").every(entry => entry.inset && entry.depth === 1));
});

test("reducers distinguish missing observations, empty sets, counts and formatted strings", () => {
  const data = [{x: null}, {x: 0}, {x: 2}, {x: 2}];
  assert.equal(summaryValue({operation: "count", source: "x"}, data), 3);
  assert.equal(summaryValue({operation: "count", source: null}, data), 4);
  assert.equal(summaryValue({operation: "median", source: "x"}, data), 2);
  assert.equal(summaryValue({operation: "count_distinct", source: "x"}, data), 2);
  assert.equal(summaryValue({operation: "sum", source: "x"}, [{x: null}]), null);
  assert.equal(summaryValue({value: "27 products", scope: "source"}, []), "27 products");
});

test("layout annotations never affect detail statistics or domains", () => {
  const pipeline = new RowPipeline();
  const result = pipeline.get({rows: source, columns: [{name: "value", type: "number", encodings: [{kind: "point", source: "value"}]}],
    options: {column_stats: true}, search: "", hidden: new Set(), sort: null, rowLayout: layout});
  assert.equal(result.stats.get("value").avg, 140 / 3);
  assert.deepEqual(result.ranges.get("value"), {min: 10, max: 100});
  assert.deepEqual(result.sorted, source);
});

test("legacy annotations are restored only for display, after filtering and sorting detail data", () => {
  const north = {render_type: "row_section", __label: "North"};
  const total = {render_type: "row_total", value: 140};
  const legacy = {legacy: [{row: north, members: [0, 1]}, {index: 0}, {index: 1}, {index: 2}, {row: total, members: [0, 1, 2]}]};
  assert.deepEqual(projectLegacy(legacy, source, [source[1]], () => false), [north, source[1], total]);
  assert.deepEqual(projectLegacy(legacy, source, [], () => false), []);
});

test("large groups project without spreading arrays into function arguments", () => {
  const data = Array.from({length: 150000}, (_, value) => ({value}));
  const large = {version: 1, groups: [{id: "all", members: data.map((_, index) => index), depth: 0, children: [], section: heading("All")}]};
  const page = projectLayout(large, data, data, 2, 100);
  assert.equal(page.entries.length, 3);
  assert.equal(page.entries[0].label, "All (cont.)");
});
